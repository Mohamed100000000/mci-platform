"""
كيان: الكورسات التدريبية (تعريف الكورس - قالب عام يُشتق منه جلسات/دورات فعلية)
"""
import uuid
from datetime import date

from sqlalchemy import String, Integer, Text, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin
from app.models.enums import CourseStatus


class Course(Base, TimestampMixin):
    """قالب الكورس: مثال STCW Basic Safety Training، Advanced Fire Fighting... إلخ"""

    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stcw_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_hours: Mapped[int] = mapped_column(Integer, default=0)
    validity_months: Mapped[int | None] = mapped_column(Integer, nullable=True)  # صلاحية الشهادة بالشهور
    max_capacity: Mapped[int] = mapped_column(Integer, default=20)

    sessions: Mapped[list["CourseSession"]] = relationship(back_populates="course")
    competency_criteria: Mapped[list["CompetencyCriteria"]] = relationship(back_populates="course")


class CourseSession(Base, TimestampMixin):
    """دورة فعلية (Instance) للكورس بتاريخ ومكان ومدرب محددين."""

    __tablename__ = "course_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    course: Mapped["Course"] = relationship(back_populates="sessions")

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    instructor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status: Mapped[CourseStatus] = mapped_column(SAEnum(CourseStatus, name="course_status"), default=CourseStatus.DRAFT)

    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="session")
    attendances: Mapped[list["Attendance"]] = relationship(back_populates="session")
