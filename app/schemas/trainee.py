import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict


class OrganizationUnitBase(BaseModel):
    name: str
    unit_type: str = "company"
    imo_number: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None


class OrganizationUnitCreate(OrganizationUnitBase):
    pass


class OrganizationUnitOut(OrganizationUnitBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class TraineeBase(BaseModel):
    full_name: str
    national_id: str | None = None
    passport_number: str | None = None
    seaman_book_number: str | None = None
    nationality: str | None = None
    date_of_birth: date | None = None
    rank: str | None = None
    email: str | None = None
    phone: str | None = None
    organization_unit_id: uuid.UUID | None = None


class TraineeCreate(TraineeBase):
    trainee_code: str


class TraineeUpdate(BaseModel):
    full_name: str | None = None
    rank: str | None = None
    email: str | None = None
    phone: str | None = None
    organization_unit_id: uuid.UUID | None = None


class TraineeOut(TraineeBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    trainee_code: str
