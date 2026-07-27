"""
كيان: مؤشر الكفاءة البحرية (Marine Competency Index - MCI)
درجة إجمالية للمتدرب على مقياس 0-1000، مبنية على الحضور + التقييمات + الشهادات السارية.
"""
import uuid
from datetime import date

from sqlalchemy import ForeignKey, Numeric, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class MCIScore(Base, TimestampMixin):
    """لقطة (snapshot) لمؤشر MCI للمتدرب في تاريخ معيّن، مع تفاصيل مكوّنات الحساب."""

    __tablename__ = "mci_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trainees.id"), nullable=False)

    calculated_on: Mapped[date] = mapped_column(Date, nullable=False)
    total_score: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)  # 0-1000

    # مكوّنات الدرجة (تفصيلية) لتسهيل الشفافية والتدقيق
    attendance_component: Mapped[float] = mapped_column(Numeric(7, 2), default=0.0)
    competency_component: Mapped[float] = mapped_column(Numeric(7, 2), default=0.0)
    certification_component: Mapped[float] = mapped_column(Numeric(7, 2), default=0.0)
    recency_component: Mapped[float] = mapped_column(Numeric(7, 2), default=0.0)

    breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # تفاصيل إضافية حرة الشكل

    trainee: Mapped["Trainee"] = relationship(back_populates="mci_scores")
