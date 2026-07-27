import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.certificate import Certificate
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.certificate import CertificateCreate, CertificateOut

router = APIRouter(prefix="/certificates", tags=["الشهادات"])


@router.get("", response_model=list[CertificateOut])
def list_certificates(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Certificate).all()


@router.post("", response_model=CertificateOut, status_code=status.HTTP_201_CREATED)
def create_certificate(
    payload: CertificateCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.TRAINING_MANAGER)),
):
    if db.query(Certificate).filter(Certificate.certificate_number == payload.certificate_number).first():
        raise HTTPException(status_code=400, detail="رقم الشهادة مستخدم بالفعل")

    certificate = Certificate(**payload.model_dump())
    db.add(certificate)
    db.commit()
    db.refresh(certificate)
    return certificate


@router.get("/trainees/{trainee_id}", response_model=list[CertificateOut])
def list_trainee_certificates(
    trainee_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return db.query(Certificate).filter(Certificate.trainee_id == trainee_id).all()
