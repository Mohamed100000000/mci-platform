"""
كيان: استبيانات رضا المتدربين (Feedback Survey) بعد انتهاء كل دورة.
"""
import uuid

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class FeedbackSurvey(Base, TimestampMixin):
    __tablename__ = "feedback_surveys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trainees.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("course_sessions.id"), nullable=False)

    instructor_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    content_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    facilities_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    trainee: Mapped["Trainee"] = relationship()
    session: Mapped["CourseSession"] = relationship()
