"""
كيان: تقييم الكفاءة (نتيجة المتدرب في معيار كفاءة معيّن ضمن دورة محددة)
"""
import uuid
from datetime import date

from sqlalchemy import ForeignKey, Numeric, Date, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin
from app.models.enums import AssessmentResult


class CompetencyAssessment(Base, TimestampMixin):
    __tablename__ = "competency_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trainees.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("course_sessions.id"), nullable=False)
    criteria_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competency_criteria.id"), nullable=False
    )
    assessor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    score: Mapped[float] = mapped_column(Numeric(6, 2), default=0.0)
    result: Mapped[AssessmentResult] = mapped_column(
        SAEnum(AssessmentResult, name="assessment_result"), default=AssessmentResult.PENDING
    )
    assessed_on: Mapped[date] = mapped_column(Date, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    trainee: Mapped["Trainee"] = relationship(back_populates="assessments")
    criteria: Mapped["CompetencyCriteria"] = relationship(back_populates="assessments")
