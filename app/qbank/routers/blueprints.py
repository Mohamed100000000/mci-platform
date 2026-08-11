import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.qbank.models import QbankExamBlueprint, QbankLearningObjective
from app.qbank.schemas import (
    BlueprintCoverageResult,
    ExamBlueprintCreate,
    ExamBlueprintOut,
    LearningObjectiveCreate,
    LearningObjectiveOut,
)
from app.qbank.services import blueprint_service

_AUTHOR_ROLES = (UserRole.ADMIN, UserRole.TRAINING_MANAGER, UserRole.INSTRUCTOR, UserRole.ASSESSOR)

router = APIRouter()


# --------------------------------------------------- Learning objectives ----

@router.get("/learning-objectives", response_model=list[LearningObjectiveOut])
def list_learning_objectives(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    stmt = select(QbankLearningObjective).where(QbankLearningObjective.course_id == course_id)
    return list(db.execute(stmt).scalars().all())


@router.post("/learning-objectives", response_model=LearningObjectiveOut, status_code=201)
def create_learning_objective(
    payload: LearningObjectiveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    lo = QbankLearningObjective(**payload.model_dump())
    db.add(lo)
    db.commit()
    db.refresh(lo)
    return lo


# ------------------------------------------------------------ Blueprints ----

@router.get("/blueprints", response_model=list[ExamBlueprintOut])
def list_blueprints(
    course_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    stmt = select(QbankExamBlueprint)
    if course_id:
        stmt = stmt.where(QbankExamBlueprint.course_id == course_id)
    return list(db.execute(stmt).scalars().all())


@router.post("/blueprints", response_model=ExamBlueprintOut, status_code=201)
def create_blueprint(
    payload: ExamBlueprintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TRAINING_MANAGER)),
):
    return blueprint_service.create_blueprint(db, payload)


@router.get("/blueprints/{blueprint_id}", response_model=ExamBlueprintOut)
def get_blueprint(
    blueprint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    blueprint = db.get(QbankExamBlueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return blueprint


@router.get("/blueprints/{blueprint_id}/coverage-check", response_model=BlueprintCoverageResult)
def coverage_check(
    blueprint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    blueprint = db.get(QbankExamBlueprint, blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    return blueprint_service.check_coverage(db, blueprint)
