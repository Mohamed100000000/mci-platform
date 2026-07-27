"""
كيان: التسجيل (ربط المتدرب بدورة تدريبية فعلية Course Session)
"""
import uuid
from datetime import date

from sqlalchemy import ForeignKey, Date, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin
from app.models.enums import EnrollmentStatus


class Enrollment(Base, TimestampMixin):
    __tablename__ = "enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trainees.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("course_sessions.id"), nullable=False)

    registration_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[EnrollmentStatus] = mapped_column(
        SAEnum(EnrollmentStatus, name="enrollment_status"), default=EnrollmentStatus.REGISTERED
    )

    trainee: Mapped["Trainee"] = relationship(back_populates="enrollments")
    session: Mapped["CourseSession"] = relationship(back_populates="enrollments")
