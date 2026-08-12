"""
تعدادات (Enums) خاصة بمنظومة بنك الأسئلة (Question Bank & Exam Engine).

ملاحظة معمارية مهمة: "content_type" يصف الوسائط المرفقة بالسؤال (نص/صورة/صوت/دمج)،
بينما "interaction_type" يصف طريقة الإجابة (اختيار من متعدد/صح-خطأ/إجابات متعددة/
مطابقة/ترتيب). "is_scenario_based" محور مستقل تمامًا عن الاثنين — أي سؤال من أي
content_type أو interaction_type يمكن أن يكون مبنيًا على سيناريو.
"""
import enum


class QuestionInteractionType(str, enum.Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    MULTIPLE_RESPONSE = "multiple_response"
    MATCHING = "matching"
    ORDERING = "ordering"


class QuestionContentType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT_IMAGE = "text_image"
    TEXT_AUDIO = "text_audio"
    IMAGE_AUDIO = "image_audio"


class QuestionDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionStatus(str, enum.Enum):
    DRAFT = "draft"
    AI_GENERATED = "ai_generated"
    AI_REVIEWED = "ai_reviewed"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    RETIRED = "retired"


class QuestionSourceType(str, enum.Enum):
    AI_GENERATED = "ai_generated"
    HUMAN_AUTHORED = "human_authored"
    IMPORTED = "imported"


class MediaType(str, enum.Enum):
    IMAGE = "image"
    AUDIO = "audio"
    ATTACHMENT = "attachment"


class MediaAttachPoint(str, enum.Enum):
    STEM = "stem"
    OPTION = "option"
    EXPLANATION = "explanation"
    SCENARIO = "scenario"


class StorageProvider(str, enum.Enum):
    S3 = "s3"
    R2 = "r2"
    LOCAL = "local"


class ReviewDecision(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    FLAG_DUPLICATE = "flag_duplicate"


class ReviewType(str, enum.Enum):
    AI_AUTO = "ai_auto"
    HUMAN = "human"


class DuplicateFlagType(str, enum.Enum):
    EXACT = "exact"
    NEAR_DUPLICATE = "near_duplicate"
    SIMILAR_SCENARIO = "similar_scenario"
    SIMILAR_ANSWER_SET = "similar_answer_set"


class DuplicateResolution(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED_DUPLICATE = "confirmed_duplicate"
    CONFIRMED_DISTINCT = "confirmed_distinct"


class GenerationBatchStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExamAttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EXPIRED = "expired"
    VOIDED = "voided"


class SourceDocumentType(str, enum.Enum):
    """نوع المصدر المرجعي الموثوق الذي يمكن تأسيس توليد الأسئلة عليه."""

    STCW = "stcw"
    IMO = "imo"
    COMPANY_SOP = "company_sop"
    COURSE_MANUAL = "course_manual"
    OTHER = "other"
