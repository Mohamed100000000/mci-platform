"""
تعدادات (Enums) مشتركة تُستخدم عبر الموديلات المختلفة.
"""
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TRAINING_MANAGER = "training_manager"
    INSTRUCTOR = "instructor"
    ASSESSOR = "assessor"
    TRAINEE = "trainee"
    VIEWER = "viewer"


class CourseStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EnrollmentStatus(str, enum.Enum):
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    ATTENDING = "attending"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AssessmentResult(str, enum.Enum):
    COMPETENT = "competent"
    NOT_YET_COMPETENT = "not_yet_competent"
    PENDING = "pending"


class CertificateStatus(str, enum.Enum):
    ISSUED = "issued"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
