"""
خدمة حساب مؤشر الكفاءة البحرية (MCI - Marine Competency Index)

المقياس: 0 - 1000
المكوّنات الأربعة (قابلة للتعديل حسب سياسة المعهد):
  1. الحضور (Attendance)        وزن 25%  -> 250 نقطة
  2. الكفاءة/التقييمات (Competency) وزن 40% -> 400 نقطة
  3. الشهادات السارية (Certification) وزن 25% -> 250 نقطة
  4. الحداثة (Recency - مدى حداثة آخر تدريب) وزن 10% -> 100 نقطة
"""
from __future__ import annotations

from datetime import date
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.assessment import CompetencyAssessment
from app.models.certificate import Certificate
from app.models.enums import AttendanceStatus, AssessmentResult, CertificateStatus

# أوزان المكوّنات (تجمع = 1000)
ATTENDANCE_WEIGHT = 250
COMPETENCY_WEIGHT = 400
CERTIFICATION_WEIGHT = 250
RECENCY_WEIGHT = 100


@dataclass
class MCIBreakdown:
    attendance_component: float = 0.0
    competency_component: float = 0.0
    certification_component: float = 0.0
    recency_component: float = 0.0
    details: dict = field(default_factory=dict)

    @property
    def total(self) -> float:
        total = (
            self.attendance_component
            + self.competency_component
            + self.certification_component
            + self.recency_component
        )
        return round(min(max(total, 0), 1000), 2)


def _compute_attendance_component(db: Session, trainee_id) -> tuple[float, dict]:
    records = db.query(Attendance).filter(Attendance.trainee_id == trainee_id).all()
    if not records:
        return 0.0, {"total_records": 0, "present_rate": 0}

    present_count = sum(1 for r in records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE))
    rate = present_count / len(records)
    score = round(rate * ATTENDANCE_WEIGHT, 2)
    return score, {"total_records": len(records), "present_rate": round(rate, 4)}


def _compute_competency_component(db: Session, trainee_id) -> tuple[float, dict]:
    assessments = (
        db.query(CompetencyAssessment).filter(CompetencyAssessment.trainee_id == trainee_id).all()
    )
    if not assessments:
        return 0.0, {"total_assessments": 0, "competent_rate": 0}

    competent_count = sum(1 for a in assessments if a.result == AssessmentResult.COMPETENT)
    # متوسط الدرجات كنسبة من الحد الأقصى لكل معيار (نفترض max_score للمعيار محمّل مسبقًا)
    normalized_scores = []
    for a in assessments:
        max_score = float(a.criteria.max_score) if a.criteria and a.criteria.max_score else 100.0
        if max_score > 0:
            normalized_scores.append(min(float(a.score) / max_score, 1.0))

    avg_normalized = sum(normalized_scores) / len(normalized_scores) if normalized_scores else 0.0
    competent_rate = competent_count / len(assessments)

    # مزيج بين متوسط الدرجات الفعلي ونسبة اجتياز معيار "كفء"
    blended = (avg_normalized * 0.7) + (competent_rate * 0.3)
    score = round(blended * COMPETENCY_WEIGHT, 2)
    return score, {
        "total_assessments": len(assessments),
        "competent_rate": round(competent_rate, 4),
        "avg_normalized_score": round(avg_normalized, 4),
    }


def _compute_certification_component(db: Session, trainee_id, as_of: date) -> tuple[float, dict]:
    certs = db.query(Certificate).filter(Certificate.trainee_id == trainee_id).all()
    if not certs:
        return 0.0, {"total_certificates": 0, "valid_count": 0}

    valid_count = 0
    for c in certs:
        is_status_ok = c.status == CertificateStatus.ISSUED
        is_not_expired = (c.expiry_date is None) or (c.expiry_date >= as_of)
        if is_status_ok and is_not_expired:
            valid_count += 1

    rate = valid_count / len(certs)
    score = round(rate * CERTIFICATION_WEIGHT, 2)
    return score, {"total_certificates": len(certs), "valid_count": valid_count}


def _compute_recency_component(db: Session, trainee_id, as_of: date) -> tuple[float, dict]:
    """كلما كان آخر نشاط تدريبي (حضور) أحدث، زادت النقاط. تتلاشى النقاط خطيًا خلال 24 شهرًا."""
    latest = (
        db.query(Attendance)
        .filter(Attendance.trainee_id == trainee_id)
        .order_by(Attendance.attendance_date.desc())
        .first()
    )
    if not latest:
        return 0.0, {"last_activity_date": None, "months_since": None}

    months_since = max((as_of - latest.attendance_date).days / 30.0, 0)
    decay_window_months = 24.0
    freshness = max(1 - (months_since / decay_window_months), 0)
    score = round(freshness * RECENCY_WEIGHT, 2)
    return score, {
        "last_activity_date": latest.attendance_date.isoformat(),
        "months_since": round(months_since, 1),
    }


def calculate_mci_score(db: Session, trainee_id, as_of: date | None = None) -> MCIBreakdown:
    """يحسب مؤشر MCI الكامل لمتدرب معيّن، مع تفاصيل كل مكوّن للشفافية والتدقيق."""
    as_of = as_of or date.today()

    attendance_score, attendance_details = _compute_attendance_component(db, trainee_id)
    competency_score, competency_details = _compute_competency_component(db, trainee_id)
    certification_score, certification_details = _compute_certification_component(db, trainee_id, as_of)
    recency_score, recency_details = _compute_recency_component(db, trainee_id, as_of)

    return MCIBreakdown(
        attendance_component=attendance_score,
        competency_component=competency_score,
        certification_component=certification_score,
        recency_component=recency_score,
        details={
            "attendance": attendance_details,
            "competency": competency_details,
            "certification": certification_details,
            "recency": recency_details,
            "calculated_on": as_of.isoformat(),
        },
    )
