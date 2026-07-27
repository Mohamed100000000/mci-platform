"""
كيان: المتدربون (بيانات أساسية + ربط بالجهة التابعين لها)
"""
import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Trainee(Base, TimestampMixin):
    __tablename__ = "trainees"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainee_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    national_id: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    passport_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    seaman_book_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(60), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    rank: Mapped[str | None] = mapped_column(String(100), nullable=True)  # الرتبة البحرية
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    organization_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organization_units.id"), nullable=True
    )
    organization_unit: Mapped["OrganizationUnit"] = relationship(back_populates="trainees")

    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="trainee")
    assessments: Mapped[list["CompetencyAssessment"]] = relationship(back_populates="trainee")
    certificates: Mapped[list["Certificate"]] = relationship(back_populates="trainee")
    mci_scores: Mapped[list["MCIScore"]] = relationship(back_populates="trainee")
