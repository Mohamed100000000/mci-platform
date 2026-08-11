"""
خدمة المراجعة: تسجيل قرار مراجعة وتحديث حالة السؤال وفق آلة الحالات
المعتمدة في الخطة (draft/ai_generated/ai_reviewed → human_review →
approved/rejected/request_changes → published → retired).
"""
import uuid

from sqlalchemy.orm import Session

from app.qbank.enums import QuestionStatus, ReviewDecision, ReviewType
from app.qbank.models import QbankQuestion, QbankReview
from app.qbank.schemas import ReviewCreate

_DECISION_TO_STATUS = {
    ReviewDecision.APPROVE: QuestionStatus.APPROVED,
    ReviewDecision.REJECT: QuestionStatus.REJECTED,
    ReviewDecision.REQUEST_CHANGES: QuestionStatus.DRAFT,
    # FLAG_DUPLICATE لا يغيّر الحالة تلقائيًا — القرار النهائي يُتخذ عبر
    # duplicate_flags.resolution (طبقة جانبية منفصلة، انظر الخطة المعتمدة §6)
}


def submit_review(
    db: Session, question: QbankQuestion, reviewer_id: uuid.UUID, payload: ReviewCreate
) -> QbankReview:
    review = QbankReview(
        question_id=question.id,
        reviewer_id=reviewer_id,
        review_type=ReviewType.HUMAN,
        decision=payload.decision,
        comments=payload.comments,
    )
    db.add(review)

    new_status = _DECISION_TO_STATUS.get(payload.decision)
    if new_status:
        question.status = new_status
        if new_status == QuestionStatus.APPROVED:
            question.approved_by_id = reviewer_id
            from sqlalchemy import func

            question.approved_at = func.now()

    db.commit()
    db.refresh(review)
    return review


def publish_question(db: Session, question: QbankQuestion) -> QbankQuestion:
    if question.status != QuestionStatus.APPROVED:
        raise ValueError("Only approved questions can be published.")
    question.status = QuestionStatus.PUBLISHED
    db.commit()
    db.refresh(question)
    return question


def retire_question(db: Session, question: QbankQuestion) -> QbankQuestion:
    question.status = QuestionStatus.RETIRED
    db.commit()
    db.refresh(question)
    return question
