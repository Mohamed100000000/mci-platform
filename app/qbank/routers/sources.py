import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.qbank.enums import SourceDocumentType
from app.qbank.models import QbankSourceDocument
from app.qbank.schemas import SourceDocumentCreate, SourceDocumentOut

_AUTHOR_ROLES = (UserRole.ADMIN, UserRole.TRAINING_MANAGER, UserRole.INSTRUCTOR)

router = APIRouter()


@router.get("/sources", response_model=list[SourceDocumentOut])
def list_source_documents(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    stmt = select(QbankSourceDocument).where(QbankSourceDocument.course_id == course_id)
    return list(db.execute(stmt).scalars().all())


@router.post("/sources", response_model=SourceDocumentOut, status_code=201)
def create_source_document(
    payload: SourceDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_AUTHOR_ROLES)),
):
    try:
        source_type = SourceDocumentType(payload.source_type)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"source_type غير صالح: {payload.source_type}")

    doc = QbankSourceDocument(
        course_id=payload.course_id,
        title=payload.title,
        source_type=source_type,
        content_text=payload.content_text,
        storage_key=payload.storage_key,
        uploaded_by_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
