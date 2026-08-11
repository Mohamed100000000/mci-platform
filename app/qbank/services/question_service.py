"""
خدمة الأسئلة: إنشاء/قراءة/تحديث + فحص التكرار الحرفي عند الإنشاء.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.qbank.enums import QuestionSourceType, QuestionStatus
from app.qbank.models import QbankOption, QbankQuestion, QbankTag
from app.qbank.schemas import QuestionCreate, QuestionUpdate
from app.qbank.services.hashing import compute_content_hash


def check_exact_duplicate(db: Session, course_id: uuid.UUID, content_hash: str) -> QbankQuestion | None:
    """يبحث عن سؤال بنفس content_hash في نفس الكورس. هذا هو منع "التكرار
    الحقيقي" المطلوب في هذه المرحلة (بدون AI)."""
    stmt = select(QbankQuestion).where(
        QbankQuestion.course_id == course_id,
        QbankQuestion.content_hash == content_hash,
    )
    return db.execute(stmt).scalars().first()


def get_or_create_tags(db: Session, tag_names: list[str]) -> list[QbankTag]:
    tags: list[QbankTag] = []
    for name in {n.strip() for n in tag_names if n.strip()}:
        existing = db.execute(select(QbankTag).where(QbankTag.name == name)).scalars().first()
        if existing:
            tags.append(existing)
        else:
            new_tag = QbankTag(name=name)
            db.add(new_tag)
            db.flush()
            tags.append(new_tag)
    return tags


def create_question(
    db: Session,
    payload: QuestionCreate,
    created_by_id: uuid.UUID,
    *,
    allow_duplicate: bool = False,
) -> tuple[QbankQuestion, QbankQuestion | None]:
    """ينشئ سؤالًا بشري المصدر. يرجع (question, duplicate_of) — إذا كان هناك
    تكرار حرفي ولم يُسمح به صراحةً (allow_duplicate=False)، يُرفع ValueError
    بدلاً من الإنشاء الصامت، بحيث لا يدخل تكرار حرفي لبنك الأسئلة دون علم
    المستخدم."""
    content_hash = compute_content_hash(payload.stem_text, payload.scenario_text)
    existing_duplicate = check_exact_duplicate(db, payload.course_id, content_hash)

    if existing_duplicate and not allow_duplicate:
        raise ValueError(
            f"Exact duplicate detected (matches question {existing_duplicate.id}). "
            "Pass allow_duplicate=true to create anyway."
        )

    question = QbankQuestion(
        course_id=payload.course_id,
        competency_criteria_id=payload.competency_criteria_id,
        learning_objective_id=payload.learning_objective_id,
        interaction_type=payload.interaction_type,
        content_type=payload.content_type,
        is_scenario_based=payload.is_scenario_based,
        difficulty=payload.difficulty,
        stem_text=payload.stem_text,
        scenario_text=payload.scenario_text,
        explanation=payload.explanation,
        source_reference=payload.source_reference,
        status=QuestionStatus.DRAFT,
        source_type=QuestionSourceType.HUMAN_AUTHORED,
        created_by_id=created_by_id,
        content_hash=content_hash,
        duplicate_of_id=existing_duplicate.id if existing_duplicate else None,
    )
    db.add(question)
    db.flush()

    for opt in payload.options:
        db.add(
            QbankOption(
                question_id=question.id,
                text=opt.text,
                is_correct=opt.is_correct,
                match_text=opt.match_text,
                order_position=opt.order_position,
                sort_order=opt.sort_order,
            )
        )

    if payload.tag_names:
        question.tags = get_or_create_tags(db, payload.tag_names)

    db.commit()
    db.refresh(question)
    return question, existing_duplicate


def update_question(db: Session, question: QbankQuestion, payload: QuestionUpdate) -> QbankQuestion:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return question


def list_questions(
    db: Session,
    *,
    course_id: uuid.UUID | None = None,
    status: QuestionStatus | None = None,
    difficulty=None,
    interaction_type=None,
    limit: int = 50,
    offset: int = 0,
) -> list[QbankQuestion]:
    stmt = select(QbankQuestion)
    if course_id:
        stmt = stmt.where(QbankQuestion.course_id == course_id)
    if status:
        stmt = stmt.where(QbankQuestion.status == status)
    if difficulty:
        stmt = stmt.where(QbankQuestion.difficulty == difficulty)
    if interaction_type:
        stmt = stmt.where(QbankQuestion.interaction_type == interaction_type)
    stmt = stmt.order_by(QbankQuestion.created_at.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())
