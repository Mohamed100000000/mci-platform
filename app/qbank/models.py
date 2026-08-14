"""
موديلات منظومة بنك الأسئلة ومحرك الامتحانات (Question Bank & Exam Engine).

قواعد معمارية:
- نفس قواعد المشروع الحالي تمامًا: SQLAlchemy 2.0 (Mapped/mapped_column)،
  UUID PK، TimestampMixin، نفس app.core.database.Base.
- كل الجداول هنا جديدة بالكامل (بادئة qbank_) — لا تعديل على أي جدول موجود.
  الربط بالجداول الحالية (courses, trainees, competency_criteria, users,
  course_sessions, competency_assessments) عبر ForeignKey فقط.
- هذا النظام منفصل تمامًا عن app/exam (اللعبة/الاختبار القديم) ولا يستورد
  منه ولا يعدّله. app/exam يستخدم قاعدة تصريحية خاصة به وغير مرتبط بـ Alembic
  الحالي (لا يظهر في target_metadata لأن app/models لا يستورده).
- عمود embedding (pgvector) مؤجَّل عمدًا لمرحلة لاحقة (كشف التكرار الدلالي
  عبر AI) تفاديًا لإضافة امتداد قاعدة بيانات غير مُفعّل بعد. بدلاً منه هناك
  عمود embedding_status نصي بسيط يوضح الحالة ("not_computed" الآن)، بحيث
  تكون إضافة العمود الحقيقي لاحقًا migration إضافية نظيفة بدون كسر شيء.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin
from app.qbank.enums import (
    DuplicateFlagType,
    DuplicateResolution,
    ExamAttemptStatus,
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
    SourceDocumentType,
    StorageProvider,
)


# ---------------------------------------------------------------- Tags ----

class QbankTag(Base, TimestampMixin):
    __tablename__ = "qbank_tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)


class QbankQuestionTag(Base):
    __tablename__ = "qbank_question_tags"

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_questions.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_tags.id", ondelete="CASCADE"), primary_key=True
    )


# --------------------------------------------------- Learning objectives ----

class QbankLearningObjective(Base, TimestampMixin):
    """هدف تعليمي مرتبط بكورس، ويمكن ربطه اختياريًا بمعيار كفاءة موجود.

    ملاحظة مهمة: عدة أسئلة يمكن أن تشير لنفس learning_objective_id عمدًا —
    هذا هو المقصود بـ"نسخ مختلفة من نفس الـcompetency بدون اعتبارها أسئلة
    متطابقة". التكرار الحقيقي يُكتشف من محتوى السؤال نفسه (content_hash /
    لاحقًا embedding) وليس من مجرد اشتراك عدة أسئلة في نفس الهدف التعليمي.
    """

    __tablename__ = "qbank_learning_objectives"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    competency_criteria_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competency_criteria.id"), nullable=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    course: Mapped["Course"] = relationship()
    competency_criteria: Mapped["CompetencyCriteria | None"] = relationship()
    questions: Mapped[list["QbankQuestion"]] = relationship(back_populates="learning_objective")

    __table_args__ = (UniqueConstraint("course_id", "code", name="uq_lo_code_per_course"),)


# ------------------------------------------------------- Generation batch ----

class QbankGenerationBatch(Base, TimestampMixin):
    """سجلّ طلب توليد أسئلة بالـAI. الجدول موجود من الآن (فارغ عمليًا) استعدادًا
    للمرحلة القادمة — لا يوجد أي استدعاء فعلي لأي AI API في هذه المرحلة."""

    __tablename__ = "qbank_generation_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    learning_objective_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_learning_objectives.id"), nullable=True
    )
    requested_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    requested_count: Mapped[int] = mapped_column(Integer, nullable=False)
    generated_count: Mapped[int] = mapped_column(Integer, default=0)
    ai_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    prompt_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_document_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[GenerationBatchStatus] = mapped_column(
        SAEnum(GenerationBatchStatus, name="qbank_generation_batch_status"),
        default=GenerationBatchStatus.QUEUED,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    questions: Mapped[list["QbankQuestion"]] = relationship(back_populates="generation_batch")


# --------------------------------------------------- Generation jobs/tasks ----
# مرحلة 2B.1: البنية التحتية لطابور التوليد. الـjob هو طلب الشخص الكبير
# ("500 سؤال لهذا الكورس")، وينقسم لعدة tasks صغيرة (≤20 سؤال لكل واحدة)
# قابلة لإعادة المحاولة فرديًا — هذا بالضبط ما يجعل pause/resume/retry
# ممكنة بدون فقدان كل الشغل عند فشل جزء صغير منه.
#
# مهم: qbank_generation_batches (من المرحلة 2A) لا تُحذف ولا تُعدَّل — تبقى
# كما هي للتوافق العكسي. الـjob/task الجديدان طبقة أعلى تُنشئ "دفعة" فعلية
# (QbankGenerationBatch) واحدة لكل task عند التنفيذ، فتُعاد نفس دالة
# generation_service.run_generation_batch() الموجودة من غير أي تعديل عليها.

class QbankGenerationJob(Base, TimestampMixin):
    __tablename__ = "qbank_generation_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True)
    requested_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    total_requested: Mapped[int] = mapped_column(Integer, nullable=False)
    total_generated: Mapped[int] = mapped_column(Integer, default=0)
    total_rejected: Mapped[int] = mapped_column(Integer, default=0)

    # مواصفة التوزيع الكاملة (صعوبة/نوع/موضوع...) — كل عنصر فيها يتحول لاحقًا
    # لـtask منفصلة عند الإنشاء.
    spec: Mapped[dict] = mapped_column(JSONB, nullable=False)

    status: Mapped[GenerationJobStatus] = mapped_column(
        SAEnum(GenerationJobStatus, name="qbank_generation_job_status"), default=GenerationJobStatus.QUEUED
    )
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # تتبّع التكلفة الإجمالية — تُحدَّث تراكميًا من كل task (المرحلة 2B.3
    # ستضيف qbank_generation_cost_log بالتفصيل؛ هذان العمودان ملخّص سريع)
    total_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    course: Mapped["Course"] = relationship()
    tasks: Mapped[list["QbankGenerationTask"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class QbankGenerationTask(Base, TimestampMixin):
    """وحدة تنفيذ واحدة صغيرة (≤20 سؤال) قابلة لإعادة المحاولة بمعزل عن
    باقي الـjob. كل task عند التنفيذ تُنشئ QbankGenerationBatch (من المرحلة
    2A) وتستدعي generation_service.run_generation_batch() الموجودة كما هي."""

    __tablename__ = "qbank_generation_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    generation_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_generation_batches.id"), nullable=True
    )

    # مواصفة هذه المهمة تحديدًا (جزء واحد من job.spec)
    learning_objective_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_learning_objectives.id"), nullable=True
    )
    interaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    content_type: Mapped[str] = mapped_column(String(30), nullable=False, default="text")
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    is_scenario_based: Mapped[bool] = mapped_column(Boolean, default=False)
    requested_count: Mapped[int] = mapped_column(Integer, nullable=False)
    source_document_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    status: Mapped[GenerationTaskStatus] = mapped_column(
        SAEnum(GenerationTaskStatus, name="qbank_generation_task_status"), default=GenerationTaskStatus.QUEUED
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    job: Mapped["QbankGenerationJob"] = relationship(back_populates="tasks")
    generation_batch: Mapped["QbankGenerationBatch | None"] = relationship()


# ---------------------------------------------------------- Source documents ----

class QbankSourceDocument(Base, TimestampMixin):
    """مصدر مرجعي موثوق (STCW/IMO/إجراءات شركة/دليل كورس) يمكن تأسيس توليد
    الأسئلة عليه، بدلاً من الاعتماد على ذاكرة النموذج فقط. content_text هو
    النص الفعلي (أو مقتطف منه) الذي يُمرَّر للـAI كسياق عند التوليد — هذا
    النص هو ما يجعل التوليد "مؤسَّسًا على مصدر" بمعنى حقيقي وليس شكليًا.

    ملاحظة نطاق هذه المرحلة: استخراج النص من ملفات PDF/Word مؤجَّل — هذا
    الجدول يقبل نصًا جاهزًا (مُلصَقًا أو مُدخلًا يدويًا) الآن. خط أنابيب
    استخراج تلقائي من الملفات المرفوعة نقطة توسعة واضحة لاحقًا، وليست
    فجوة في هذا التصميم — storage_key موجود من الآن لهذا الغرض.
    """

    __tablename__ = "qbank_source_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    source_type: Mapped[SourceDocumentType] = mapped_column(
        SAEnum(SourceDocumentType, name="qbank_source_document_type"), nullable=False
    )
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    course: Mapped["Course"] = relationship()


# ------------------------------------------------------------- Questions ----

class QbankQuestion(Base, TimestampMixin):
    __tablename__ = "qbank_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # الربط بالكيانات الموجودة فعليًا (لا تعديل عليها، FK فقط)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True)
    competency_criteria_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competency_criteria.id"), nullable=True, index=True
    )
    learning_objective_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_learning_objectives.id"), nullable=True
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    generation_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_generation_batches.id"), nullable=True
    )
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_questions.id"), nullable=True
    )
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_source_documents.id"), nullable=True
    )

    # تصنيف السؤال
    interaction_type: Mapped[QuestionInteractionType] = mapped_column(
        SAEnum(QuestionInteractionType, name="qbank_interaction_type"), nullable=False
    )
    content_type: Mapped[QuestionContentType] = mapped_column(
        SAEnum(QuestionContentType, name="qbank_content_type"), nullable=False, default=QuestionContentType.TEXT
    )
    is_scenario_based: Mapped[bool] = mapped_column(Boolean, default=False)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        SAEnum(QuestionDifficulty, name="qbank_difficulty"), nullable=False, default=QuestionDifficulty.MEDIUM
    )

    # محتوى السؤال
    stem_text: Mapped[str] = mapped_column(Text, nullable=False)
    scenario_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # دورة الحياة
    status: Mapped[QuestionStatus] = mapped_column(
        SAEnum(QuestionStatus, name="qbank_question_status"), nullable=False, default=QuestionStatus.DRAFT, index=True
    )
    source_type: Mapped[QuestionSourceType] = mapped_column(
        SAEnum(QuestionSourceType, name="qbank_source_type"), nullable=False
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # كشف التكرار — الطبقة الأولى (تكرار حقيقي/حرفي) فعّالة من الآن، بدون AI.
    # الطبقة الثانية (تكرار دلالي عبر embeddings) مؤجّلة — انظر التعليق أعلى الملف.
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    embedding_status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_computed")
    quality_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # إحصائيات (تُحدَّث لاحقًا مع محرك الامتحان الفعلي — أعمدة موجودة من الآن)
    times_shown: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    discrimination_index: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)

    # العلاقات
    course: Mapped["Course"] = relationship()
    competency_criteria: Mapped["CompetencyCriteria | None"] = relationship()
    learning_objective: Mapped["QbankLearningObjective | None"] = relationship(back_populates="questions")
    generation_batch: Mapped["QbankGenerationBatch | None"] = relationship(back_populates="questions")
    duplicate_of: Mapped["QbankQuestion | None"] = relationship(remote_side=[id])
    source_document: Mapped["QbankSourceDocument | None"] = relationship()

    options: Mapped[list["QbankOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="QbankOption.sort_order"
    )
    media_assets: Mapped[list["QbankMediaAsset"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    reviews: Mapped[list["QbankReview"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    tags: Mapped[list["QbankTag"]] = relationship(secondary="qbank_question_tags")

    __table_args__ = (
        UniqueConstraint("content_hash", "course_id", name="uq_qbank_question_hash_per_course"),
    )


class QbankOption(Base):
    """خيار إجابة. يخدم الأنواع الأربعة:
    - MCQ / MULTIPLE_RESPONSE: is_correct هو المحدِّد (أكثر من صف صحيح مسموح
      لـ multiple_response).
    - TRUE_FALSE: صفّان فقط (True/False)، is_correct يحدد الصحيح.
    - MATCHING: كل صف = زوج (text = العنصر الأيسر، match_text = تطابقه
      الصحيح على اليمين). is_correct غير مستخدم هنا.
    - ORDERING: كل صف = عنصر، order_position = ترتيبه الصحيح. is_correct
     غير مستخدم هنا.
    """

    __tablename__ = "qbank_options"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_questions.id", ondelete="CASCADE"), nullable=False
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    match_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # MATCHING فقط
    order_position: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ORDERING فقط
    is_distractor_quality_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    question: Mapped["QbankQuestion"] = relationship(back_populates="options")


# --------------------------------------------------------- Media assets ----

class QbankMediaAsset(Base, TimestampMixin):
    """بيانات وصفية للملف فقط — الملف نفسه في تخزين كانات خارجي (S3-compatible)،
    غير مخزَّن داخل قاعدة البيانات."""

    __tablename__ = "qbank_media_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_questions.id", ondelete="CASCADE"), nullable=True
    )
    option_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_options.id", ondelete="CASCADE"), nullable=True
    )

    attach_point: Mapped[MediaAttachPoint] = mapped_column(SAEnum(MediaAttachPoint, name="qbank_media_attach_point"))
    media_type: Mapped[MediaType] = mapped_column(SAEnum(MediaType, name="qbank_media_type"))
    storage_provider: Mapped[StorageProvider] = mapped_column(
        SAEnum(StorageProvider, name="qbank_storage_provider"), default=StorageProvider.LOCAL
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    alt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)

    question: Mapped["QbankQuestion | None"] = relationship(back_populates="media_assets")


# ---------------------------------------------------------------- Review ----

class QbankReview(Base):
    __tablename__ = "qbank_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_questions.id", ondelete="CASCADE"), nullable=False
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    review_type: Mapped[ReviewType] = mapped_column(SAEnum(ReviewType, name="qbank_review_type"))
    decision: Mapped[ReviewDecision] = mapped_column(SAEnum(ReviewDecision, name="qbank_review_decision"))
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    question: Mapped["QbankQuestion"] = relationship(back_populates="reviews")


class QbankDuplicateFlag(Base):
    __tablename__ = "qbank_duplicate_flags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_questions.id", ondelete="CASCADE"), nullable=False
    )
    candidate_duplicate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_questions.id", ondelete="CASCADE"), nullable=False
    )
    similarity_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    flag_type: Mapped[DuplicateFlagType] = mapped_column(SAEnum(DuplicateFlagType, name="qbank_duplicate_flag_type"))
    resolution: Mapped[DuplicateResolution] = mapped_column(
        SAEnum(DuplicateResolution, name="qbank_duplicate_resolution"), default=DuplicateResolution.PENDING
    )
    resolved_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ------------------------------------------------------------ Blueprints ----

class QbankExamBlueprint(Base, TimestampMixin):
    __tablename__ = "qbank_exam_blueprints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty_distribution: Mapped[dict] = mapped_column(JSONB, nullable=False)
    interaction_type_distribution: Mapped[dict] = mapped_column(JSONB, nullable=False)
    content_type_distribution: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    competency_distribution: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    passing_score_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=60.0)
    time_limit_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    course: Mapped["Course"] = relationship()


# ------------------------------------------------------- Exam attempts  ----

class QbankExamAttempt(Base):
    """محاولة امتحان حقيقية لمتدرب حقيقي (منفصلة تمامًا عن ExamAttempt في
    app/exam القديم). لا تُنشأ ولا تُملأ أي أسئلة فعلية في هذه المرحلة —
    الجدول جاهز فقط لمرحلة محرك توليد الامتحان القادمة."""

    __tablename__ = "qbank_exam_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trainees.id"), nullable=False, index=True)
    blueprint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_exam_blueprints.id"), nullable=False
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("course_sessions.id"), nullable=True
    )
    competency_assessment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("competency_assessments.id"), nullable=True
    )

    status: Mapped[ExamAttemptStatus] = mapped_column(
        SAEnum(ExamAttemptStatus, name="qbank_exam_attempt_status"), default=ExamAttemptStatus.IN_PROGRESS
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_questions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    trainee: Mapped["Trainee"] = relationship()
    blueprint: Mapped["QbankExamBlueprint"] = relationship()
    questions: Mapped[list["QbankExamQuestion"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class QbankExamQuestion(Base):
    """لقطة (snapshot) لأي أسئلة عُرضت ضمن محاولة امتحان معيّنة."""

    __tablename__ = "qbank_exam_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_exam_attempts.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("qbank_questions.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    selected_option_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    attempt: Mapped["QbankExamAttempt"] = relationship(back_populates="questions")
    question: Mapped["QbankQuestion"] = relationship()

    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_qbank_exam_question_per_attempt"),)


class QbankTraineeQuestionHistory(Base):
    """سجلّ مبسّط ومفهرَس لكل (متدرب, سؤال) لتسريع منع التكرار عند توليد
    امتحان جديد — بدون الحاجة لمسح كل محاولات الامتحان القديمة."""

    __tablename__ = "qbank_trainee_question_history"

    trainee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trainees.id"), primary_key=True)
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qbank_questions.id"), primary_key=True
    )
    last_shown_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    times_shown: Mapped[int] = mapped_column(Integer, default=1)
