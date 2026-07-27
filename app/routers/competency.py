import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.competency import CompetencyCriteria
from app.models.assessment import CompetencyAssessment
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.competency import (
    CompetencyCriteriaCreate,
    CompetencyCriteriaOut,
    CompetencyAssessmentCreate,
    CompetencyAssessmentOut,
)

router = APIRouter(tags=["الكفاءات والتقييمات"])


@router.get("/courses/{course_id}/criteria", response_model=list[CompetencyCriteriaOut])
def list_criteria(course_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(CompetencyCriteria).filter(CompetencyCriteria.course_id == course_id).all()


@router.post("/criteria", response_model=CompetencyCriteriaOut, status_code=status.HTTP_201_CREATED)
def create_criteria(
    payload: CompetencyCriteriaCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.TRAINING_MANAGER)),
):
    criteria = CompetencyCriteria(**payload.model_dump())
    db.add(criteria)
    db.commit()
    db.refresh(criteria)
    return criteria


@router.post("/assessments", response_model=CompetencyAssessmentOut, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: CompetencyAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.INSTRUCTOR, UserRole.ASSESSOR)),
):
    assessment = CompetencyAssessment(**payload.model_dump(), assessor_id=current_user.id)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/trainees/{trainee_id}/assessments", response_model=list[CompetencyAssessmentOut])
def list_trainee_assessments(
    trainee_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return db.query(CompetencyAssessment).filter(CompetencyAssessment.trainee_id == trainee_id).all()
