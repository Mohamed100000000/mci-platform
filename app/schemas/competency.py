import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict

from app.models.enums import AssessmentResult


class CompetencyCriteriaBase(BaseModel):
    course_id: uuid.UUID
    code: str
    title: str
    description: str | None = None
    weight: float = 1.0
    max_score: float = 100.0


class CompetencyCriteriaCreate(CompetencyCriteriaBase):
    pass


class CompetencyCriteriaOut(CompetencyCriteriaBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class CompetencyAssessmentBase(BaseModel):
    trainee_id: uuid.UUID
    session_id: uuid.UUID
    criteria_id: uuid.UUID
    score: float
    result: AssessmentResult = AssessmentResult.PENDING
    assessed_on: date
    remarks: str | None = None


class CompetencyAssessmentCreate(CompetencyAssessmentBase):
    pass


class CompetencyAssessmentOut(CompetencyAssessmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    assessor_id: uuid.UUID | None = None
