from __future__ import annotations

from app.schemas.ats_schemas import ResumeInformation
from app.services.ai_service import ai_provider


def extract_resume_information(resume_text: str) -> ResumeInformation:
    return ai_provider.extract_resume_information(resume_text)