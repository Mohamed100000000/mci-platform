"""
Pydantic schemas لمنظومة بنك الأسئلة.

قاعدة أمان مهمة (يُبنى عليها لاحقًا في مرحلة محرك الامتحان): QuestionOptionOut
لا يحمل is_correct إطلاقًا. QuestionOptionAdminOut (يحمل الإجابة الصحيحة)
مخصص فقط لواجهات الإدارة/المراجعة، وليس لأي مسار قد يصل إليه متدرب.
"""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.qbank.enums import (
    DuplicateFlagType,
    DuplicateResolution,
    GenerationBatchStatus,
    GenerationJobStatus,
    GenerationTaskStatus,
    MediaAttachPoint,
    MediaType,
    QuestionContentType,
    QuestionDifficulty,
    QuestionInteractionType,
    QuestionSourceType,
    QuestionStatus,
    ReviewDecision,
    ReviewType,
    StorageProvider,
)


# --------------------------------------------------------------- Tags ----

class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str


# ---------------------------------------------------- Learning objectives ----

class LearningObjectiveCreate(BaseModel):
    course_id: uuid.UUID
    competency_criteria_id: uuid.UUID | None = None
    code: str = Field(..., max_length=50)
    description: str


class LearningObjectiveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    competency_criteria_id: uuid.UUID | None
    code: str
    description: str


# ------------------------------------------------------------- Options ----

class OptionAdminCreate(BaseModel):
    """للإنشاء عبر واجهات الإدارة/التأليف — تتضمن الإجابة الصحيحة."""

    text: str
    is_correct: bool = False
    match_text: str | None = None
    order_position: int | None = None
    sort_order: int = 0


class OptionAdminOut(BaseModel):
    """للمراجعين/الإداريين فقط — تحمل is_correct."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    text: str
    is_correct: bool
    match_text: str | None
    order_position: int | None
    is_distractor_quality_flagged: bool
    sort_order: int


class OptionPublicOut(BaseModel):
    """لأي مسار قد يصل إليه متدرب أثناء امتحان — بدون أي إشارة للإجابة الصحيحة."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    text: str
    sort_order: int


# --------------------------------------------------------- Media assets ----

class MediaAssetCreate(BaseModel):
    question_id: uuid.UUID | None = None
    option_id: uuid.UUID | None = None
    attach_point: MediaAttachPoint
    media_type: MediaType
    storage_provider: StorageProvider = StorageProvider.LOCAL
    storage_key: str
    mime_type: str
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    alt_text: str | None = None
    transcript: str | None = None


class MediaAssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID | None
    option_id: uuid.UUID | None
    attach_point: MediaAttachPoint
    media_type: MediaType
    storage_provider: StorageProvider
    storage_key: str
    mime_type: str
    file_size_bytes: int | None
    alt_text: str | None
    transcript: str | None


# ----------------------------------------------------------- Questions ----

class QuestionCreate(BaseModel):
    """إنشاء سؤال بشري المصدر (source_type يُضبط داخليًا = human_authored).
    التوليد بالـAI له مسار منفصل في مرحلة قادمة."""

    course_id: uuid.UUID
    competency_criteria_id: uuid.UUID | None = None
    learning_objective_id: uuid.UUID | None = None
    interaction_type: QuestionInteractionType
    content_type: QuestionContentType = QuestionContentType.TEXT
    is_scenario_based: bool = False
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    stem_text: str
    scenario_text: str | None = None
    explanation: str | None = None
    source_reference: str | None = None
    tag_names: list[str] = Field(default_factory=list)
    options: list[OptionAdminCreate] = Field(default_factory=list)


class QuestionUpdate(BaseModel):
    competency_criteria_id: uuid.UUID | None = None
    learning_objective_id: uuid.UUID | None = None
    difficulty: QuestionDifficulty | None = None
    stem_text: str | None = None
    scenario_text: str | None = None
    explanation: str | None = None
    source_reference: str | None = None
    status: QuestionStatus | None = None


class QuestionAdminOut(BaseModel):
    """عرض إداري/مراجعة كامل — يتضمن الإجابات الصحيحة. لا يُستخدم أبدًا في
    مسار امتحان فعلي لمتدرب."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    competency_criteria_id: uuid.UUID | None
    learning_objective_id: uuid.UUID | None
    interaction_type: QuestionInteractionType
    content_type: QuestionContentType
    is_scenario_based: bool
    difficulty: QuestionDifficulty
    stem_text: str
    scenario_text: str | None
    explanation: str | None
    source_reference: str | None
    status: QuestionStatus
    source_type: QuestionSourceType
    content_hash: str
    embedding_status: str
    quality_score: float | None
    times_shown: int
    times_correct: int
    discrimination_index: float | None
    created_at: datetime
    updated_at: datetime
    options: list[OptionAdminOut] = Field(default_factory=list)
    media_assets: list[MediaAssetOut] = Field(default_factory=list)
    tags: list[TagOut] = Field(default_factory=list)


class QuestionListItemOut(BaseModel):
    """صف مختصر لجدول القائمة — بدون الخيارات الكاملة."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    interaction_type: QuestionInteractionType
    content_type: QuestionContentType
    difficulty: QuestionDifficulty
    status: QuestionStatus
    source_type: QuestionSourceType
    stem_text: str
    times_shown: int
    times_correct: int
    created_at: datetime


class DuplicateCheckResult(BaseModel):
    is_exact_duplicate: bool
    duplicate_question_id: uuid.UUID | None = None


# -------------------------------------------------------------- Review ----

class ReviewCreate(BaseModel):
    decision: ReviewDecision
    comments: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID
    reviewer_id: uuid.UUID
    review_type: ReviewType
    decision: ReviewDecision
    comments: str | None
    created_at: datetime


class DuplicateFlagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID
    candidate_duplicate_id: uuid.UUID
    similarity_score: float | None
    flag_type: DuplicateFlagType
    resolution: DuplicateResolution


class DuplicateFlagResolve(BaseModel):
    resolution: DuplicateResolution


# --------------------------------------------------- Generation batches ----
# (Schemas جاهزة للمرحلة القادمة — لا يوجد أي endpoint يستدعي AI فعليًا الآن)

class GenerationBatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    learning_objective_id: uuid.UUID | None
    requested_count: int
    generated_count: int
    ai_model: str | None
    prompt_version: str | None
    input_tokens: int | None
    output_tokens: int | None
    error_message: str | None
    status: GenerationBatchStatus
    created_at: datetime


class GenerationBatchCreate(BaseModel):
    """طلب توليد دفعة أسئلة. count محدود عمدًا بحد أقصى صغير في هذه المرحلة
    (2A) — التوليد واسع النطاق (5000+) مؤجَّل صراحة للمرحلة القادمة بعد
    مراجعة نتائج هذه المرحلة."""

    course_id: uuid.UUID
    learning_objective_id: uuid.UUID | None = None
    interaction_type: QuestionInteractionType
    content_type: QuestionContentType = QuestionContentType.TEXT
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    is_scenario_based: bool = False
    count: int = Field(..., ge=1, le=20)
    source_document_ids: list[uuid.UUID] = Field(default_factory=list)


# ------------------------------------------ Generation jobs (2B.1) ----

class GenerationTaskSpec(BaseModel):
    """مواصفة مهمة واحدة داخل job — تصبح صف QbankGenerationTask عند الإنشاء."""

    learning_objective_id: uuid.UUID | None = None
    interaction_type: QuestionInteractionType
    content_type: QuestionContentType = QuestionContentType.TEXT
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    is_scenario_based: bool = False
    count: int = Field(..., ge=1, le=20)
    source_document_ids: list[uuid.UUID] = Field(default_factory=list)


class GenerationJobCreate(BaseModel):
    """طلب توليد كبير — ينقسم لعدة مهام صغيرة قابلة لإعادة المحاولة فرديًا.
    لا حد أقصى صارم على عدد المهام هنا (بخلاف GenerationBatchCreate) لأن
    كل مهمة تُنفَّذ بمعزل عن الأخرى عبر الطابور، لا في نفس الطلب المتزامن."""

    course_id: uuid.UUID
    tasks: list[GenerationTaskSpec] = Field(..., min_length=1)


class GenerationTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    job_id: uuid.UUID
    generation_batch_id: uuid.UUID | None
    learning_objective_id: uuid.UUID | None
    interaction_type: str
    content_type: str
    difficulty: str
    requested_count: int
    status: GenerationTaskStatus
    retry_count: int
    last_error: str | None
    created_at: datetime


class GenerationJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    total_requested: int
    total_generated: int
    total_rejected: int
    status: GenerationJobStatus
    total_input_tokens: int
    total_output_tokens: int
    created_at: datetime
    completed_at: datetime | None
    tasks: list[GenerationTaskOut] = Field(default_factory=list)


class GenerationJobSummary(BaseModel):
    """ملخص مختصر لحالة job — لصفحة مراقبة الدفعات (Batch Monitor) لاحقًا،
    بدون تحميل كل صفوف tasks في كل استعلام حالة."""

    id: uuid.UUID
    status: GenerationJobStatus
    total_requested: int
    total_generated: int
    tasks_total: int
    tasks_completed: int
    tasks_failed: int
    tasks_running: int
    tasks_queued: int


# ------------------------------------------------------- Source documents ----

class SourceDocumentCreate(BaseModel):
    course_id: uuid.UUID
    title: str
    source_type: str  # قيمة SourceDocumentType
    content_text: str = Field(..., min_length=20)
    storage_key: str | None = None


class SourceDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    source_type: str
    storage_key: str | None
    created_at: datetime


# --------------------------------------------------------- Blueprints ----

class ExamBlueprintCreate(BaseModel):
    course_id: uuid.UUID
    name: str
    total_questions: int
    difficulty_distribution: dict[str, float]
    interaction_type_distribution: dict[str, float]
    content_type_distribution: dict[str, float] | None = None
    competency_distribution: dict[str, float] | None = None
    passing_score_pct: float = 60.0
    time_limit_seconds: int | None = None


class ExamBlueprintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID
    name: str
    total_questions: int
    difficulty_distribution: dict[str, Any]
    interaction_type_distribution: dict[str, Any]
    content_type_distribution: dict[str, Any] | None
    competency_distribution: dict[str, Any] | None
    passing_score_pct: float
    time_limit_seconds: int | None
    is_active: bool


class BlueprintCoverageResult(BaseModel):
    """نتيجة التحقق من كفاية بنك الأسئلة المعتمد لتغطية توزيع Blueprint معيّن.
    Endpoint جاهز من الآن لأنه استعلام عد بسيط (بدون AI)، مفيد فورًا حتى قبل
    وجود محرك توليد الامتحان الفعلي."""

    is_sufficient: bool
    total_approved_available: int
    total_required: int
    gaps: list[dict[str, Any]] = Field(default_factory=list)
