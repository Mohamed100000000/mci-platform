import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.qbank.enums import GenerationBatchStatus
from app.qbank.models import QbankGenerationBatch
from app.qbank.schemas import GenerationBatchCreate, GenerationBatchOut
from app.qbank.services import generation_service

_GENERATION_ROLES = (UserRole.ADMIN, UserRole.TRAINING_MANAGER)

router = APIRouter()


@router.post("/generation/batches", response_model=GenerationBatchOut, status_code=201)
def create_generation_batch(
    payload: GenerationBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    batch = QbankGenerationBatch(
        course_id=payload.course_id,
        learning_objective_id=payload.learning_objective_id,
        requested_by_id=current_user.id,
        requested_count=payload.count,
        source_document_ids=[str(i) for i in payload.source_document_ids] or None,
        status=GenerationBatchStatus.QUEUED,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    batch = generation_service.run_generation_batch(
        db,
        batch,
        interaction_type=payload.interaction_type.value,
        content_type=payload.content_type.value,
        difficulty=payload.difficulty.value,
        is_scenario_based=payload.is_scenario_based,
    )
    return batch


@router.get("/generation/batches/{batch_id}", response_model=GenerationBatchOut)
def get_generation_batch(
    batch_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    batch = db.get(QbankGenerationBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Generation batch not found")
    return batch


@router.get("/generation/batches", response_model=list[GenerationBatchOut])
def list_generation_batches(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    from sqlalchemy import select

    stmt = select(QbankGenerationBatch).where(QbankGenerationBatch.course_id == course_id).order_by(
        QbankGenerationBatch.created_at.desc()
    )
    return list(db.execute(stmt).scalars().all())
