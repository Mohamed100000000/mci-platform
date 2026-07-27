"""
كيان: الجهة/السفينة/القسم التابع له المتدرب (Organization Unit)
"""
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class OrganizationUnit(Base, TimestampMixin):
    """يمثل سفينة، شركة تشغيل، أو قسم داخل المعهد يتبع له المتدربون."""

    __tablename__ = "organization_units"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), default="company")  # company | vessel | department
    imo_number: Mapped[str | None] = mapped_column(String(20), nullable=True)  # لو سفينة
    contact_email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    trainees: Mapped[list["Trainee"]] = relationship(back_populates="organization_unit")
