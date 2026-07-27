import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict

from app.models.enums import EnrollmentStatus, AttendanceStatus


class EnrollmentBase(BaseModel):
    trainee_id: uuid.UUID
    session_id: uuid.UUID
    registration_date: date
    status: EnrollmentStatus = EnrollmentStatus.REGISTERED


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentOut(EnrollmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class AttendanceBase(BaseModel):
    trainee_id: uuid.UUID
    session_id: uuid.UUID
    attendance_date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: str | None = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceBulkCreate(BaseModel):
    """لتسجيل حضور عدة متدربين دفعة واحدة لنفس الجلسة والتاريخ."""
    session_id: uuid.UUID
    attendance_date: date
    records: list[dict]  # [{"trainee_id": "...", "status": "present", "notes": "..."}]


class AttendanceOut(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    recorded_by_id: uuid.UUID | None = None
