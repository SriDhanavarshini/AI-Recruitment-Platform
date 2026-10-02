from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


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
    name: str
    domain: str | None = None


class CompanyOut(CompanyCreate):
    id: int
    owner_id: int


class JobCreate(BaseModel):
    company_id: int
    title: str
    description: str
    required_skills: list[str] = Field(default_factory=list)
    required_experience: str | None = None
    location: str | None = None
    employment_type: str = "FULL_TIME"
    status: str = "OPEN"


class JobOut(JobCreate):
    id: int
    created_at: datetime | None = None


class ResumeUpload(BaseModel):
    candidate_id: int
    file_url: str
    storage_path: str
    extracted_skills: list[str] = Field(default_factory=list)


class ApplicationCreate(BaseModel):
    candidate_id: int
    job_id: int
    resume_id: int


class ApplicationOut(ApplicationCreate):
    id: int
    status: str
    ats_score: float = 0.0
    created_at: datetime | None = None


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
