import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

from app.models.enums import CertificateStatus


class CertificateBase(BaseModel):
    trainee_id: uuid.UUID
    session_id: uuid.UUID
    issue_date: date
    expiry_date: date | None = None
    status: CertificateStatus = CertificateStatus.PENDING
    file_reference: str | None = None


class CertificateCreate(CertificateBase):
    certificate_number: str


class CertificateOut(CertificateBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    certificate_number: str


class MCIScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    trainee_id: uuid.UUID
    calculated_on: date
    total_score: float
    attendance_component: float
    competency_component: float
    certification_component: float
    recency_component: float
    breakdown: dict | None = None
    created_at: datetime
