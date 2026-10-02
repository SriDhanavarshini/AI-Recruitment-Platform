from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResumeInformation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    skills: list[str]
    education: list[str]
    experience: str
    projects: list[str]

    @field_validator("skills", "education", "projects")
    @classmethod
    def remove_empty_entries(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value.strip() for value in values if value.strip()))


class ATSProcessResponse(BaseModel):
    id: UUID
    application_id: UUID
    score: float = Field(ge=0, le=100)
    matching_skills: list[str]
    missing_skills: list[str]
    extracted_skills: list[str]
    extracted_education: list[str]
    extracted_experience: str
    extracted_projects: list[str]
    explanation: str
    created_at: datetime
    semantic: float | None = Field(default=None, ge=0, le=100)
    keyword: float | None = Field(default=None, ge=0, le=100)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)