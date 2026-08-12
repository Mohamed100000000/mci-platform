"""
خدمة توليد الأسئلة بالـAI — قلب المرحلة 2A.

تدفق العمل لكل دفعة:
  1. جلب نصوص المصادر الموثوقة إن وُجدت (تأسيس حقيقي، ليس من الذاكرة فقط)
  2. جلب أسئلة موجودة لنفس الهدف التعليمي (لتقليل التكرار السطحي)
  3. بناء الـprompt (نقي، لا آثار جانبية) واستدعاء مزوّد الـAI
  4. لكل سؤال في الاستجابة: تحقق صارم من البنية → إن فشل: رفض وتسجيل السبب
  5. فحص تكرار حرفي (content_hash) → إن كان مكررًا: تجاهل بصمت (متوقع في
     التوليد بالجملة، ليس خطأ يستحق تنبيه المستخدم لكل حالة)
  6. فحوصات جودة قاعدية → quality_score يُخزَّن على السؤال
  7. إنشاء السؤال بحالة status=ai_generated (لن يدخل published مباشرة أبدًا)
  8. فحص تكرار شبه-دلالي (نصي) بعد الإنشاء، وتسجيل أي تشابه كـflag
  9. تحديث الدفعة: generated_count, input/output tokens, status, completed_at
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.qbank.ai import provider
from app.qbank.ai.prompts import PROMPT_VERSION, build_generation_prompt
from app.qbank.enums import GenerationBatchStatus, QuestionSourceType, QuestionStatus
from app.qbank.models import (
    QbankGenerationBatch,
    QbankOption,
    QbankQuestion,
    QbankSourceDocument,
)
from app.qbank.services import near_duplicate_service, question_service, quality_service
from app.qbank.services.generation_validation import validate_generated_question
from app.qbank.services.hashing import compute_content_hash


def _load_context(db: Session, batch: QbankGenerationBatch) -> tuple[str, str, str | None]:
    from app.models.course import Course
    from app.models.competency import CompetencyCriteria
    from app.qbank.models import QbankLearningObjective

    course = db.get(Course, batch.course_id)
    lo = db.get(QbankLearningObjective, batch.learning_objective_id) if batch.learning_objective_id else None
    competency_title = None
    if lo and lo.competency_criteria_id:
        criteria = db.get(CompetencyCriteria, lo.competency_criteria_id)
        competency_title = criteria.title if criteria else None
    return course.title, (lo.description if lo else "غير محدد"), competency_title


def run_generation_batch(
    db: Session,
    batch: QbankGenerationBatch,
    *,
    interaction_type: str,
    content_type: str,
    difficulty: str,
    is_scenario_based: bool,
) -> QbankGenerationBatch:
    batch.status = GenerationBatchStatus.RUNNING
    db.commit()

    try:
        course_title, lo_description, competency_title = _load_context(db, batch)

        source_texts: list[str] = []
        if batch.source_document_ids:
            for doc_id in batch.source_document_ids:
                doc = db.get(QbankSourceDocument, uuid.UUID(doc_id))
                if doc:
                    source_texts.append(doc.content_text)

        existing_stems = []
        if batch.learning_objective_id:
            stmt = select(QbankQuestion.stem_text).where(
                QbankQuestion.learning_objective_id == batch.learning_objective_id
            ).limit(30)
            existing_stems = list(db.execute(stmt).scalars().all())

        prompt = build_generation_prompt(
            course_title=course_title,
            learning_objective=lo_description,
            competency_title=competency_title,
            difficulty=difficulty,
            interaction_type=interaction_type,
            content_type=content_type,
            is_scenario_based=is_scenario_based,
            count=batch.requested_count,
            source_texts=source_texts,
            existing_stems=existing_stems,
        )

        result = provider.generate(prompt)
        raw_questions = result.raw_json.get("questions", [])

        created_count = 0
        rejected_reasons: list[str] = []
        single_source_id = uuid.UUID(batch.source_document_ids[0]) if batch.source_document_ids and len(batch.source_document_ids) == 1 else None

        for item in raw_questions:
            validation = validate_generated_question(item, interaction_type)
            if not validation.is_valid:
                rejected_reasons.append("; ".join(validation.errors))
                continue

            content_hash = compute_content_hash(item["stem_text"], item.get("scenario_text"))
            if question_service.check_exact_duplicate(db, batch.course_id, content_hash):
                continue  # تكرار حرفي متوقع أثناء التوليد بالجملة — يُتجاهل بصمت

            quality = quality_service.run_quality_checks(item, interaction_type)

            question = QbankQuestion(
                course_id=batch.course_id,
                learning_objective_id=batch.learning_objective_id,
                interaction_type=interaction_type,
                content_type=content_type,
                is_scenario_based=is_scenario_based,
                difficulty=difficulty,
                stem_text=item["stem_text"],
                scenario_text=item.get("scenario_text"),
                explanation=item.get("explanation"),
                source_reference=item.get("source_reference"),
                source_document_id=single_source_id,
                status=QuestionStatus.AI_GENERATED,
                source_type=QuestionSourceType.AI_GENERATED,
                generation_batch_id=batch.id,
                content_hash=content_hash,
                quality_score=quality.score,
            )
            db.add(question)
            db.flush()

            for opt in item.get("options", []):
                db.add(
                    QbankOption(
                        question_id=question.id,
                        text=opt["text"],
                        is_correct=bool(opt.get("is_correct", False)),
                        match_text=opt.get("match_text"),
                        order_position=opt.get("order_position"),
                    )
                )

            db.flush()
            near_duplicate_service.flag_near_duplicates(db, question)
            created_count += 1

        batch.generated_count = created_count
        batch.ai_model = result.model
        batch.prompt_version = PROMPT_VERSION
        batch.input_tokens = result.input_tokens
        batch.output_tokens = result.output_tokens
        batch.status = GenerationBatchStatus.COMPLETED
        if rejected_reasons:
            batch.error_message = f"{len(rejected_reasons)} سؤال مرفوض من {len(raw_questions)}: " + " | ".join(rejected_reasons[:5])
        db.commit()

    except provider.GenerationError as exc:
        batch.status = GenerationBatchStatus.FAILED
        batch.error_message = str(exc)
        db.commit()
    except Exception as exc:  # noqa: BLE001 — أي خطأ غير متوقع يُسجَّل بدلاً من تعليق الطلب
        batch.status = GenerationBatchStatus.FAILED
        batch.error_message = f"خطأ غير متوقع: {exc}"
        db.commit()

    db.refresh(batch)
    return batch
