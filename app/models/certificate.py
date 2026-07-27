"""
كيان: الشهادات (تتبع الشهادات الصادرة للمتدربين - الطباعة تتم خارجيًا، النظام يتتبع فقط)
"""
import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin
from app.models.enums import CertificateStatus


class Certificate(Base, TimestampMixin):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_number: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    trainee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trainees.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("course_sessions.id"), nullable=False)

    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[CertificateStatus] = mapped_column(
        SAEnum(CertificateStatus, name="certificate_status"), default=CertificateStatus.PENDING
    )
    file_reference: Mapped[str | None] = mapped_column(String(300), nullable=True)  # مسار/رابط ملف الشهادة الممسوحة

    trainee: Mapped["Trainee"] = relationship(back_populates="certificates")
    session: Mapped["CourseSession"] = relationship()
