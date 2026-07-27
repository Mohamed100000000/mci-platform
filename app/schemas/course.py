import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict

from app.models.enums import CourseStatus


class CourseBase(BaseModel):
    code: str
    title: str
    description: str | None = None
    stcw_reference: str | None = None
    duration_hours: int = 0
    validity_months: int | None = None
    max_capacity: int = 20


class CourseCreate(CourseBase):
    pass


class CourseOut(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class CourseSessionBase(BaseModel):
    course_id: uuid.UUID
    start_date: date
    end_date: date
    location: str | None = None
    instructor_id: uuid.UUID | None = None
    status: CourseStatus = CourseStatus.DRAFT


class CourseSessionCreate(CourseSessionBase):
    pass


class CourseSessionOut(CourseSessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
