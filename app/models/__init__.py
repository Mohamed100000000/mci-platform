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
]
