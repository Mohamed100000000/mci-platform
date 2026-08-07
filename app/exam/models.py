"""
SQLAlchemy models for the AZDA Captain Challenge exam engine.

Integration notes
------------------
- Drop this file into your MCI backend as `app/exam/models.py` (or merge the
  classes into your existing `models.py`).
- `Base` should be the SAME declarative base your MCI project already uses,
  so these tables land in the same metadata / Alembic autogenerate scope.
  Replace the import below with your project's actual Base import, e.g.:
      from app.db.base import Base
- `Trainee.id` below is a stand-in FK target. Point `ExamAttempt.trainee_id`
  at your existing Trainee/User model's primary key instead.
- All monetary/organizational multi-tenancy (institute_id) is included so
  this can be sold to other training institutes, not just AZDA, without a
  schema change later.
"""

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

# --- Replace with your project's actual Base ---
from sqlalchemy.orm import declarative_base

Base = declarative_base()
# -------------------------------------------------


def gen_uuid():
    return uuid.uuid4()


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class AttemptStatus(str, enum.Enum):
    in_progress = "in_progress"
    submitted = "submitted"
    expired = "expired"
    voided = "voided"  # e.g. flagged for cheating and invalidated


class Institute(Base):
    """Multi-tenant root. Each training institute using the platform."""

    __tablename__ = "exam_institutes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    logo_base64 = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subjects = relationship("Subject", back_populates="institute")


class Subject(Base):
    __tablename__ = "exam_subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    institute_id = Column(UUID(as_uuid=True), ForeignKey("exam_institutes.id"), nullable=False)
    code = Column(String(50), nullable=False)  # e.g. "PST", "GMDSS"
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    icon = Column(String(16), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)

    institute = relationship("Institute", back_populates="subjects")
    levels = relationship("Level", back_populates="subject", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("institute_id", "code", name="uq_subject_code_per_institute"),)


class Level(Base):
    __tablename__ = "exam_levels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("exam_subjects.id"), nullable=False)
    index = Column(Integer, nullable=False)  # 0=easy,1=medium,2=hard
    difficulty = Column(Enum(Difficulty), nullable=False)
    pass_threshold_pct = Column(Integer, default=60, nullable=False)
    time_limit_seconds = Column(Integer, default=20)  # per-question timer
    questions_per_attempt = Column(Integer, default=20)  # how many Qs pulled per exam
    negative_marking = Column(Boolean, default=False)

    subject = relationship("Subject", back_populates="levels")
    questions = relationship("Question", back_populates="level", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("subject_id", "index", name="uq_level_index_per_subject"),)


class Question(Base):
    __tablename__ = "exam_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    level_id = Column(UUID(as_uuid=True), ForeignKey("exam_levels.id"), nullable=False)
    text_ar = Column(Text, nullable=False)
    text_en = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # Item-analysis fields, updated by a background job after each attempt
    times_shown = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    level = relationship("Level", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")


class Option(Base):
    __tablename__ = "exam_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    question_id = Column(UUID(as_uuid=True), ForeignKey("exam_questions.id"), nullable=False)
    text_ar = Column(Text, nullable=False)
    text_en = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0)

    question = relationship("Question", back_populates="options")


class ExamAttempt(Base):
    """One exam session for one trainee on one (subject, level)."""

    __tablename__ = "exam_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    # --- point this at your real trainee/user table ---
    trainee_id = Column(UUID(as_uuid=True), nullable=False)
    trainee_name = Column(String(255), nullable=False)
    trainee_email = Column(String(255), nullable=False)
    trainee_id_number = Column(String(100), nullable=False)  # national ID / passport
    # ----------------------------------------------------
    level_id = Column(UUID(as_uuid=True), ForeignKey("exam_levels.id"), nullable=False)
    status = Column(Enum(AttemptStatus), default=AttemptStatus.in_progress, nullable=False)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)  # server-enforced deadline
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    score = Column(Integer, nullable=True)  # correct answers
    total_questions = Column(Integer, nullable=True)
    pct = Column(Integer, nullable=True)
    passed = Column(Boolean, nullable=True)

    # anti-cheat telemetry
    tab_switch_count = Column(Integer, default=0)
    fullscreen_exit_count = Column(Integer, default=0)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    flagged_for_review = Column(Boolean, default=False)

    level = relationship("Level")
    answers = relationship("ExamAnswer", back_populates="attempt", cascade="all, delete-orphan")
    certificate = relationship("Certificate", back_populates="attempt", uselist=False)


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("exam_attempts.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("exam_questions.id"), nullable=False)
    selected_option_id = Column(UUID(as_uuid=True), ForeignKey("exam_options.id"), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    time_taken_seconds = Column(Integer, nullable=True)

    attempt = relationship("ExamAttempt", back_populates="answers")

    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_answer_per_question"),)


class Certificate(Base):
    __tablename__ = "exam_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("exam_attempts.id"), nullable=False, unique=True)
    verification_code = Column(String(32), nullable=False, unique=True, index=True)
    pdf_path = Column(String(512), nullable=True)  # or S3 key
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)
    revoked_reason = Column(String(255), nullable=True)

    attempt = relationship("ExamAttempt", back_populates="certificate")
