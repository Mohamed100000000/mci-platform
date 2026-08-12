"""
كشف التكرار شبه-الدلالي (near-duplicate) باستخدام تشابه النصوص —
حل مؤقت مُعلَن صراحة، وليس التصميم النهائي.

قرار معماري مسجَّل هنا عمدًا: الخطة المعتمدة تطلب كشف تكرار دلالي حقيقي
عبر embeddings + pgvector، لكن هذه البنية التحتية لم تُفعَّل بعد (قرار
المرحلة الأولى). بدلاً من الانتظار أو اختراع حل مؤقت غير موثّق، هذه
الطبقة تستخدم difflib.SequenceMatcher (تشابه نصي حرفي/شبه-حرفي) كطبقة
وسطى فعلية الآن تلتقط "نفس السؤال بصياغة مختلفة قليلاً" — لكنها لا تلتقط
تكرارًا بنفس المعنى بصياغة مختلفة جذريًا (وهذا بالضبط ما ستضيفه
embeddings لاحقًا). كل قرار من هنا يُسجَّل بـflag_type=NEAR_DUPLICATE
ليكون واضحًا للمراجع البشري أنه ترشيح آلي وليس يقينًا.
"""
import difflib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.qbank.enums import DuplicateFlagType, QuestionStatus
from app.qbank.models import QbankDuplicateFlag, QbankQuestion
from app.qbank.services.hashing import normalize_text

# عتبة التشابه — فوقها يُعتبر السؤال قريبًا بما يكفي ليستحق مراجعة بشرية.
_NEAR_DUPLICATE_THRESHOLD = 0.82


def find_near_duplicates(db: Session, question: QbankQuestion, *, limit_pool: int = 500) -> list[tuple[QbankQuestion, float]]:
    """يقارن سؤالًا جديدًا بأسئلة الكورس نفسه (المعتمدة/المنشورة/قيد
    المراجعة) عبر تشابه النص. يرجّع فقط ما فوق العتبة."""
    stmt = (
        select(QbankQuestion)
        .where(
            QbankQuestion.course_id == question.course_id,
            QbankQuestion.id != question.id,
            QbankQuestion.status.in_(
                [
                    QuestionStatus.APPROVED,
                    QuestionStatus.PUBLISHED,
                    QuestionStatus.HUMAN_REVIEW,
                    QuestionStatus.AI_REVIEWED,
                    QuestionStatus.AI_GENERATED,
                ]
            ),
        )
        .limit(limit_pool)
    )
    candidates = db.execute(stmt).scalars().all()

    target = normalize_text(question.stem_text)
    matches: list[tuple[QbankQuestion, float]] = []
    for candidate in candidates:
        ratio = difflib.SequenceMatcher(None, target, normalize_text(candidate.stem_text)).ratio()
        if ratio >= _NEAR_DUPLICATE_THRESHOLD:
            matches.append((candidate, ratio))
    return matches


def flag_near_duplicates(db: Session, question: QbankQuestion) -> list[QbankDuplicateFlag]:
    flags = []
    for candidate, ratio in find_near_duplicates(db, question):
        flag = QbankDuplicateFlag(
            question_id=question.id,
            candidate_duplicate_id=candidate.id,
            similarity_score=round(ratio, 4),
            flag_type=DuplicateFlagType.NEAR_DUPLICATE,
        )
        db.add(flag)
        flags.append(flag)
    if flags:
        db.commit()
    return flags
