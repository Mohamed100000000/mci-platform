"""
كيان: معايير الكفاءة (Competency Criteria) - معايير ديناميكية لكل كورس
تُستخدم في تقييم المتدربين وفي حساب مؤشر MCI.
"""
import uuid

from sqlalchemy import String, Text, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class CompetencyCriteria(Base, TimestampMixin):
    """معيار كفاءة مرتبط بكورس معيّن، له وزن (weight) يُستخدم في حساب MCI."""

    __tablename__ = "competency_criteria"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    course: Mapped["Course"] = relationship(back_populates="competency_criteria")

    code: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Numeric(5, 2), default=1.0)  # وزن المعيار ضمن الكورس
    max_score: Mapped[float] = mapped_column(Numeric(6, 2), default=100.0)

    assessments: Mapped[list["CompetencyAssessment"]] = relationship(back_populates="criteria")
