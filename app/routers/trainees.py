import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.trainee import Trainee
from app.models.organization import OrganizationUnit
from app.models.user import User
from app.schemas.trainee import (
    TraineeCreate,
    TraineeUpdate,
    TraineeOut,
    OrganizationUnitCreate,
    OrganizationUnitOut,
)

router = APIRouter(prefix="/trainees", tags=["المتدربون"])
org_router = APIRouter(prefix="/organization-units", tags=["الجهات/السفن"])


@router.get("", response_model=list[TraineeOut])
def list_trainees(
    search: str | None = Query(default=None, description="بحث بالاسم أو الكود"),
    organization_unit_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Trainee)
    if search:
        like = f"%{search}%"
        query = query.filter((Trainee.full_name.ilike(like)) | (Trainee.trainee_code.ilike(like)))
    if organization_unit_id:
        query = query.filter(Trainee.organization_unit_id == organization_unit_id)
    return query.order_by(Trainee.full_name).all()


@router.get("/{trainee_id}", response_model=TraineeOut)
def get_trainee(trainee_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    trainee = db.get(Trainee, trainee_id)
    if not trainee:
        raise HTTPException(status_code=404, detail="المتدرب غير موجود")
    return trainee


@router.post("", response_model=TraineeOut, status_code=status.HTTP_201_CREATED)
def create_trainee(payload: TraineeCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    if db.query(Trainee).filter(Trainee.trainee_code == payload.trainee_code).first():
        raise HTTPException(status_code=400, detail="كود المتدرب مستخدم بالفعل")

    trainee = Trainee(**payload.model_dump())
    db.add(trainee)
    db.commit()
    db.refresh(trainee)
    return trainee


@router.patch("/{trainee_id}", response_model=TraineeOut)
def update_trainee(
    trainee_id: uuid.UUID,
    payload: TraineeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    trainee = db.get(Trainee, trainee_id)
    if not trainee:
        raise HTTPException(status_code=404, detail="المتدرب غير موجود")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(trainee, field, value)

    db.commit()
    db.refresh(trainee)
    return trainee


@org_router.get("", response_model=list[OrganizationUnitOut])
def list_organization_units(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(OrganizationUnit).order_by(OrganizationUnit.name).all()


@org_router.post("", response_model=OrganizationUnitOut, status_code=status.HTTP_201_CREATED)
def create_organization_unit(
    payload: OrganizationUnitCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    unit = OrganizationUnit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit
