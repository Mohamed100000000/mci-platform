"""
خدمة Exam Blueprint: إنشاء/قراءة + التحقق من كفاية بنك الأسئلة المعتمد
لتغطية التوزيع المطلوب (coverage check). هذا الفحص استعلام عدّ بسيط، لا
يحتاج AI، ومفيد من الآن حتى قبل وجود محرك توليد الامتحان الفعلي."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.qbank.enums import QuestionStatus
from app.qbank.models import QbankExamBlueprint, QbankQuestion
from app.qbank.schemas import BlueprintCoverageResult, ExamBlueprintCreate


def create_blueprint(db: Session, payload: ExamBlueprintCreate) -> QbankExamBlueprint:
    blueprint = QbankExamBlueprint(**payload.model_dump())
    db.add(blueprint)
    db.commit()
    db.refresh(blueprint)
    return blueprint


def check_coverage(db: Session, blueprint: QbankExamBlueprint) -> BlueprintCoverageResult:
    """يتحقق فقط من العدد الإجمالي للأسئلة المعتمدة/المنشورة المتاحة لكل
    خلية صعوبة مطلوبة في التوزيع، مقارنةǶ بالعدد المطلوب فعليًا. التحقق
    التفصيلي (تقاطع صعوبة "× now تفاعل × نوع محتوى معًا) يُبنى في مرحلة
    محرك توليد الامتحان القادمة فوق هذا الأساس نفسه."""
    available_statuses = [QuestionStatus.APPROVED, QuestionStatus.PUBLISHED]

    total_available = db.execute(
        select(func.count(QbankQuestion.id)).where(
            QbankQuestion.course_id == blueprint.course_id,
            QbankQuestion.status.in_(available_statuses),
        )
    ).scalar_one()

    gaps = []
    for difficulty_key, ratio in blueprint.difficulty_distribution.items():
        required = round(blueprint.total_questions * ratio)
        available = db.execute(
            select(func.count(QbankQuestion.id)).where(
                QbankQuestion.course_id == blueprint.course_id,
                QbankQuestion.status.in_(available_statuses),
                QbankQuestion.difficulty == difficulty_key,
            )
        ).scalar_one()
        if available < required:
            gaps.append(
                {
                    "dimension": "difficulty",
                    "value": difficulty_key,
                    "required": required,
                    "available": available,
                    "shortfall": required - available,
                }
            )

    return BlueprintCoverageResult(
        is_sufficient=len(gaps) == 0 and total_available >= blueprint.total_questions,
        total_approved_available=total_available,
        total_required=blueprint.total_questions,
        gaps=gaps,
    )
