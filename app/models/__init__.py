"""
تجميع كل الموديلات في مكان واحد حتى تتعرف SQLAlchemy على كل العلاقات
(مهم جدًا لعمل Alembic migrations بشكل صحيح).
"""
from app.models.user import User  # noqa: F401
from app.models.organization import OrganizationUnit  # noqa: F401
from app.models.trainee import Trainee  # noqa: F401
from app.models.course import Course, CourseSession  # noqa: F401
from app.models.enrollment import Enrollment  # noqa: F401
from app.models.attendance import Attendance  # noqa: F401
from app.models.competency import CompetencyCriteria  # noqa: F401
from app.models.assessment import CompetencyAssessment  # noqa: F401
from app.models.certificate import Certificate  # noqa: F401
from app.models.mci_score import MCIScore  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.feedback import FeedbackSurvey  # noqa: F401

# منظومة بنك الأسئلة ومحرك الامتحانات (qbank) — جداول جديدة بالكامل، بادئة
# qbank_، لا تُعدّل أي جدول أعلاه. هذا الاستيراد ضروري فقط حتى يكتشف
# Alembic autogenerate الجداول الجديدة (نفس سبب وجود هذا الملف أصلًا).
from app.qbank.models import (  # noqa: F401
    QbankDuplicateFlag,
    QbankExamAttempt,
    QbankExamBlueprint,
    QbankExamQuestion,
    QbankGenerationBatch,
    QbankLearningObjective,
    QbankMediaAsset,
    QbankOption,
    QbankQuestion,
    QbankQuestionTag,
    QbankReview,
    QbankSourceDocument,
    QbankTag,
    QbankTraineeQuestionHistory,
)

__all__ = [
    "User",
    "OrganizationUnit",
    "Trainee",
    "Course",
    "CourseSession",
    "Enrollment",
    "Attendance",
    "CompetencyCriteria",
    "CompetencyAssessment",
    "Certificate",
    "MCIScore",
    "AuditLog",
    "FeedbackSurvey",
    "QbankTag",
    "QbankQuestionTag",
    "QbankLearningObjective",
    "QbankGenerationBatch",
    "QbankQuestion",
    "QbankOption",
    "QbankMediaAsset",
    "QbankReview",
    "QbankSourceDocument",
    "QbankDuplicateFlag",
    "QbankExamBlueprint",
    "QbankExamAttempt",
    "QbankExamQuestion",
    "QbankTraineeQuestionHistory",
]
