from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: str
    full_name: str
    role: str = "CANDIDATE"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class CompanyOut(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: datetime


class JobCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    required_skills: list[str] = Field(default_factory=list)
    required_experience: str | None = None
    location: str | None = None
    employment_type: Literal["FULL_TIME", "PART_TIME", "INTERNSHIP", "CONTRACT"]

    @field_validator("title", "description")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class JobUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    required_skills: list[str] | None = None
    required_experience: str | None = None
    location: str | None = None
    employment_type: Literal["FULL_TIME", "PART_TIME", "INTERNSHIP", "CONTRACT"] | None = None

    @field_validator("title", "description")
    @classmethod
    def reject_blank_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @model_validator(mode="after")
    def require_valid_updates(self):
        if not self.model_fields_set:
            raise ValueError("at least one job field must be provided")
        non_nullable = {"company_id", "title", "description", "required_skills", "employment_type"}
        if any(name in self.model_fields_set and getattr(self, name) is None for name in non_nullable):
            raise ValueError("provided job fields cannot be null")
        return self


class JobStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["OPEN", "CLOSED"]


class JobOut(BaseModel):
    id: UUID
    company_id: UUID
    title: str
    description: str
    required_skills: list[str]
    required_experience: str | None = None
    location: str | None = None
    employment_type: Literal["FULL_TIME", "PART_TIME", "INTERNSHIP", "CONTRACT"]
    status: Literal["OPEN", "CLOSED"]
    created_at: datetime
    updated_at: datetime


class OpenJobOut(BaseModel):
    id: UUID
    title: str
    description: str
    required_skills: list[str]
    required_experience: str | None = None
    location: str | None = None
    employment_type: Literal["FULL_TIME", "PART_TIME", "INTERNSHIP", "CONTRACT"]
    status: Literal["OPEN"]
    created_at: datetime


class ResumeUpload(BaseModel):
    id: UUID
    candidate_id: UUID
    file_name: str
    file_url: str
    uploaded_at: datetime


class ApplicationCreate(BaseModel):
    job_id: UUID
    resume_id: UUID


class ApplicationJobInfo(BaseModel):
    id: UUID
    title: str
    description: str
    required_skills: list[str]
    required_experience: str | None = None
    location: str | None = None
    employment_type: str
    status: str


class ApplicationOut(BaseModel):
    id: UUID
    job_id: UUID
    resume_id: UUID
    status: str
    applied_at: datetime
    job: ApplicationJobInfo | None = None


class ATSResultCreate(BaseModel):
    application_id: int
    score: float
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    relevant_experience: str | None = None
    extracted_resume_data: dict[str, Any] = Field(default_factory=dict)
    explanation: str | None = None


class ATSResultOut(ATSResultCreate):
    id: int
    created_at: datetime | None = None


class QuestionCreate(BaseModel):
    question: str
    type: str
    topic: str
    difficulty: str
    options: list[str] = Field(default_factory=list)
    correct_answer: str | None = None
    explanation: str | None = None
    marks: int = 1


class QuestionOut(QuestionCreate):
    id: int
    approved: bool = False
    created_at: datetime | None = None


class AssessmentCreate(BaseModel):
    name: str
    duration_minutes: int = 60
    passing_score: float = 60.0
    marks: int = 100
    difficulty: str = "MEDIUM"
    number_of_questions: int = 40


class AssessmentOut(AssessmentCreate):
    id: int
    created_at: datetime | None = None


class CodingSubmissionCreate(BaseModel):
    candidate_id: int
    problem_id: int
    language: str
    code: str


class CodingSubmissionOut(CodingSubmissionCreate):
    id: int
    passed_tests: int = 0
    failed_tests: int = 0
    execution_time_ms: int = 0
    memory_kb: int = 0
    score: float = 0.0
    created_at: datetime | None = None


class ProctoringEventCreate(BaseModel):
    assessment_attempt_id: int
    event_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class InterviewCreate(BaseModel):
    candidate_id: int
    category: str = "TECHNICAL"
    max_questions: int = 5


class InterviewReportOut(BaseModel):
    id: int
    interview_id: int
    technical_score: float = 0.0
    domain_score: float = 0.0
    communication_score: float = 0.0
    relevance_score: float = 0.0
    overall_score: float = 0.0
    strengths: list[str] = Field(default_factory=list)
    areas_for_improvement: list[str] = Field(default_factory=list)
    question_evaluations: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = None


class ReapplicationRule(BaseModel):
    candidate_id: int
    job_id: int
    rejection_date: date
    eligible_reapply_date: date
