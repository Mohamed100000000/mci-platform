import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.qbank.enums import QuestionStatus
from app.qbank.models import QbankDuplicateFlag, QbankQuestion
from app.qbank.schemas import DuplicateFlagOut, DuplicateFlagResolve, ReviewCreate, ReviewOut
from app.qbank.services import review_service

_REVIEWER_ROLES = (UserRole.ADMIN, UserRole.TRAINING_MANAGER, UserRole.ASSESSOR)

router = APIRouter()


@router.get("/review/queue", response_model=list[dict])
def review_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_REVIEWER_ROLES)),
):
    """الأسئلة التي تنتظر مراجعة بشرية. في هذه المرحلة هذا يعني عمليًا
    draft/ai_generated/ai_reviewed التي لم تُعتمد بعد — لا يوجد توليد AI
    فعلي الآن، لذلك القائمة ستعرض الأسئلة المؤلَّفة يدويًا في status=draft
    التي طلب مؤلفها مراجعتها."""
    stmt = select(QbankQuestion).where(
        QbankQuestion.status.in_(
            [QuestionStatus.DRAFT, QuestionStatus.AI_GENERATED, QuestionStatus.AI_REVIEWED, QuestionStatus.HUMAN_REVIEW]
        )
    ).order_by(QbankQuestion.created_at.asc())
    questions = db.execute(stmt).scalars().all()
    return [
        {
            "id": str(q.id),
            "course_id": str(q.course_id),
            "stem_text": q.stem_text,
            "status": q.status.value,
            "difficulty": q.difficulty.value,
            "created_at": q.created_at.isoformat(),
        }
        for q in questions
    ]


@router.post("/review/{question_id}/decision", response_model=ReviewOut)
def submit_review(
    question_id: uuid.UUID,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_REVIEWER_ROLES)),
):
    question = db.get(QbankQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return review_service.submit_review(db, question, current_user.id, payload)


@router.post("/questions/{question_id}/publish", response_model=dict)
def publish_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TRAINING_MANAGER)),
):
    question = db.get(QbankQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    try:
        review_service.publish_question(db, question)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"id": str(question.id), "status": question.status.value}


@router.get("/review/duplicates", response_model=list[DuplicateFlagOut])
def list_duplicate_flags(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_REVIEWER_ROLES)),
):
    stmt = select(QbankDuplicateFlag).order_by(QbankDuplicateFlag.created_at.desc())
    return list(db.execute(stmt).scalars().all())


@router.post("/review/duplicates/{flag_id}/resolve", response_model=DuplicateFlagOut)
def resolve_duplicate_flag(
    flag_id: uuid.UUID,
    payload: DuplicateFlagResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_REVIEWER_ROLES)),
):
    flag = db.get(QbankDuplicateFlag, flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Duplicate flag not found")
    flag.resolution = payload.resolution
    flag.resolved_by_id = current_user.id
    db.commit()
    db.refresh(flag)
    return flag
