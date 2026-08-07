"""
Pydantic schemas for the exam API.

SECURITY-CRITICAL: `OptionOut` deliberately has NO `is_correct` field.
`QuestionOut` deliberately has NO field indicating the right answer.
These are the only shapes ever sent to the client during an active exam.
Never reuse the SQLAlchemy model objects directly in a response_model —
always go through these schemas so a future refactor can't accidentally
leak the answer key into the browser.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---------- Public catalog (browsing, before login) ----------

class SubjectOut(BaseModel):
    id: UUID
    code: str
    name_ar: str
    name_en: str
    icon: Optional[str]

    class Config:
        orm_mode = True


class LevelOut(BaseModel):
    id: UUID
    index: int
    difficulty: str
    questions_per_attempt: int
    time_limit_seconds: int

    class Config:
        orm_mode = True


# ---------- Starting an exam ----------

class StartExamRequest(BaseModel):
    trainee_name: str = Field(..., min_length=2, max_length=255)
    trainee_email: EmailStr
    trainee_id_number: str = Field(..., min_length=3, max_length=100)
    level_id: UUID


class OptionOut(BaseModel):
    """No `is_correct` — this is what gets sent to the browser."""
    id: UUID
    text: str  # already localized server-side based on Accept-Language / lang param

    class Config:
        orm_mode = True


class QuestionOut(BaseModel):
    """No answer-key field — this is what gets sent to the browser."""
    id: UUID
    text: str
    options: List[OptionOut]

    class Config:
        orm_mode = True


class ExamSessionOut(BaseModel):
    attempt_id: UUID
    subject_code: str
    level_index: int
    expires_at: datetime
    time_limit_seconds_per_question: int
    questions: List[QuestionOut]


# ---------- Answering ----------

class SubmitAnswerRequest(BaseModel):
    question_id: UUID
    selected_option_id: Optional[UUID] = None  # null = timed out / skipped
    time_taken_seconds: Optional[int] = None


class SubmitAnswerAck(BaseModel):
    """Deliberately does not say whether the answer was correct."""
    question_id: UUID
    received: bool = True


# ---------- Anti-cheat telemetry ----------

class CheatSignalRequest(BaseModel):
    event: str  # "tab_hidden" | "fullscreen_exit" | "devtools_open" (best-effort)


# ---------- Final result (only revealed after submit) ----------

class ExamResultOut(BaseModel):
    attempt_id: UUID
    score: int
    total_questions: int
    pct: int
    passed: bool
    rank_label: str
    certificate_id: Optional[UUID]
    certificate_url: Optional[str]


# ---------- Certificate verification (public) ----------

class CertificateVerifyOut(BaseModel):
    valid: bool
    trainee_name: Optional[str] = None
    subject_name_en: Optional[str] = None
    level_difficulty: Optional[str] = None
    pct: Optional[int] = None
    issued_at: Optional[datetime] = None
    institute_name: Optional[str] = None
    revoked: bool = False
