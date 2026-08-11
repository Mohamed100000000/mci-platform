import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.qbank.enums import QuestionDifficulty, QuestionInteractionType, QuestionStatus
from app.qbank.models import QbankQuestion
from app.qbank.schemas import (
    DuplicateCheckResult,
    QuestionAdminOut,
    QuestionCreate,
    QuestionListItemOut,
    QuestionUpdate,
)
from app.qbank.services import question_service
from app.qbank.services.hashing import compute_content_hash

# جميع مسارات بنك الأسئلة الإدارية مقصورة على الأدوار التي تؤلف/تراجع محتوى.
# لا يوجد أي مسار هنا يصل إليه متدرب مباشرة — ذلك محجوز لمرحلة محرك الامتحان
# القادمة (endpoints منفصلة تمامًا، بحمولة استجابة مختلفة لا تحمل إجابات).
_AUTHOR_ROLES = (UserRole.ADMIN, UserRole.TRAINING_MANAGER, UserRole.INSTRUCTOR, UserRole.ASSESSOR)

router = APIRouter()


@router.get("/questions", response_model=list[QuestionListItemOut])
def list_questions(
    course_id: uuid.UUID | None = None,
    status: QuestionStatus | None = None,
    difficulty: QuestionDifficulty | None = None,
    interaction_type: QuestionInteractionType | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    return question_service.list_questions(
        db,
        course_id=course_id,
        status=status,
        difficulty=difficulty,
        interaction_type=interaction_type,
        limit=limit,
        offset=offset,
    )


@router.post("/questions/check-duplicate", response_model=DuplicateCheckResult)
def check_duplicate(
    course_id: uuid.UUID,
    stem_text: str,
    scenario_text: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    """فحص تكرار حرفي قبل الإنشاء — مفيد لواجهة التأليف لتنبيه المستخدم
    فورًا أثناء الكتابة، بدون الحاجة لمحاولة إنشاء ثم فشل."""
    content_hash = compute_content_hash(stem_text, scenario_text)
    duplicate = question_service.check_exact_duplicate(db, course_id, content_hash)
    return DuplicateCheckResult(
        is_exact_duplicate=duplicate is not None,
        duplicate_question_id=duplicate.id if duplicate else None,
    )


@router.post("/questions", response_model=QuestionAdminOut, status_code=201)
def create_question(
    payload: QuestionCreate,
    allow_duplicate: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    try:
        question, _duplicate = question_service.create_question(
            db, payload, current_user.id, allow_duplicate=allow_duplicate
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return question


@router.get("/questions/{question_id}", response_model=QuestionAdminOut)
def get_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    question = db.get(QbankQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.patch("/questions/{question_id}", response_model=QuestionAdminOut)
def update_question(
    question_id: uuid.UUID,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    question = db.get(QbankQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question_service.update_question(db, question, payload)


@router.delete("/questions/{question_id}", status_code=204)
def retire_question_endpoint(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TRAINING_MANAGER)),
):
    """حذف "ناعم" فقط — ينقل الحالة إلى retired، لا يحذف الصف فعليًا (يحافظ
    على السجل التاريخي/الإحصائي)."""
    from app.qbank.services import review_service

    question = db.get(QbankQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    review_service.retire_question(db, question)
    return None
