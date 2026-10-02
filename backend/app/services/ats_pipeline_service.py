from __future__ import annotations

import re
from typing import Any, Callable
from uuid import UUID
from urllib.parse import unquote, urlsplit

from app.core.config import get_settings
from app.core.supabase import supabase
from app.schemas.ats_schemas import ResumeInformation
from app.services.ai_extraction_service import extract_resume_information
from app.services.ats_scoring_service import ats_score
from app.services.resume_extraction_service import ResumeExtractionError, extract_resume_text

APPLICATION_COLUMNS = "id, candidate_id, job_id, resume_id, status, applied_at"
RESUME_COLUMNS = "id, candidate_id, file_name, file_url"
JOB_COLUMNS = "id, company_id, title, description, required_skills, required_experience"
ATS_RESULT_COLUMNS = (
    "id, application_id, score, matching_skills, missing_skills, extracted_skills, "
    "extracted_education, extracted_experience, extracted_projects, explanation, created_at"
)


class ATSNotFoundError(Exception):
    pass


class ATSForbiddenError(Exception):
    pass


class ATSConflictError(Exception):
    pass


class ATSProcessingError(Exception):
    pass


class ATSInputError(Exception):
    pass


class ATSPipelineService:
    def __init__(
        self,
        database: Any = None,
        text_extractor: Callable[[str, bytes], str] | None = None,
        information_extractor: Callable[[str], Any] | None = None,
        scorer: Callable[[str, str], dict[str, Any]] | None = None,
    ):
        self.database = database or supabase
        self.text_extractor = text_extractor or extract_resume_text
        self.information_extractor = information_extractor or extract_resume_information
        self.scorer = scorer or ats_score

    def process_application(self, application_id: UUID, current_user: dict[str, Any]) -> dict[str, Any]:
        application, resume, job = self._load_application_context(application_id, current_user)
        try:
            existing = (
                self.database.table("ats_results")
                .select(ATS_RESULT_COLUMNS)
                .eq("application_id", str(application_id))
                .maybe_single()
                .execute()
            )
            if existing.data is not None:
                raise ATSConflictError("An ATS result already exists for this application")

            file_bytes = self._download_resume(resume["file_url"], application["candidate_id"])
            try:
                resume_text = self.text_extractor(resume["file_name"], file_bytes)
            except ResumeExtractionError as error:
                raise ATSInputError(str(error)) from None
            try:
                raw_information = self.information_extractor(resume_text)
            except Exception:
                raise ATSProcessingError("AI resume information extraction failed") from None
            try:
                information = ResumeInformation.model_validate(raw_information)
            except Exception:
                raise ATSProcessingError("AI provider returned invalid resume information") from None
            information = _ground_information(information, resume_text)
            job_description = _build_job_description(job)
            score = self.scorer(resume_text, job_description)
            matching_skills, missing_skills = _match_required_skills(
                job.get("required_skills") or [], information.skills
            )
            result_payload = {
                "application_id": str(application_id),
                "score": score["score"],
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "extracted_skills": information.skills,
                "extracted_education": information.education,
                "extracted_experience": information.experience,
                "extracted_projects": information.projects,
                "explanation": _build_explanation(
                    score, matching_skills, missing_skills, information, job_description
                ),
            }
            inserted = (
                self.database.table("ats_results")
                .insert(result_payload)
                .select(ATS_RESULT_COLUMNS)
                .single()
                .execute()
            )
            if inserted.data is None:
                raise ATSProcessingError("ATS result was not returned after insertion")
            return {
                **inserted.data,
                "semantic": score["semantic"],
                "keyword": score["keyword"],
                "matched_keywords": score["matched_keywords"],
                "missing_keywords": score["missing_keywords"],
            }
        except (ATSConflictError, ATSInputError, ATSProcessingError):
            raise
        except Exception as error:
            if getattr(error, "code", None) == "23505":
                raise ATSConflictError("An ATS result already exists for this application") from None
            raise ATSProcessingError("ATS processing failed") from None

    def get_result(self, application_id: UUID, current_user: dict[str, Any]) -> dict[str, Any]:
        self._load_application_context(application_id, current_user, load_resume=False)
        try:
            result = (
                self.database.table("ats_results")
                .select(ATS_RESULT_COLUMNS)
                .eq("application_id", str(application_id))
                .maybe_single()
                .execute()
            )
        except Exception:
            raise ATSProcessingError("Could not retrieve ATS result") from None
        if result.data is None:
            raise ATSNotFoundError("ATS result not found")
        return result.data

    def _load_application_context(
        self,
        application_id: UUID,
        current_user: dict[str, Any],
        load_resume: bool = True,
    ) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any]]:
        if current_user.get("role") not in {"CANDIDATE", "HR"}:
            raise ATSForbiddenError("Candidate or HR role required")
        try:
            app_result = (
                self.database.table("applications")
                .select(APPLICATION_COLUMNS)
                .eq("id", str(application_id))
                .maybe_single()
                .execute()
            )
            application = app_result.data
            if application is None:
                raise ATSNotFoundError("Application not found")
            if current_user["role"] == "CANDIDATE" and str(application["candidate_id"]) != str(current_user["id"]):
                raise ATSNotFoundError("Application not found")

            job_result = (
                self.database.table("jobs")
                .select(JOB_COLUMNS)
                .eq("id", str(application["job_id"]))
                .maybe_single()
                .execute()
            )
            job = job_result.data
            if job is None:
                raise ATSNotFoundError("Application job not found")
            if current_user["role"] == "HR":
                company_result = (
                    self.database.table("companies")
                    .select("id")
                    .eq("id", str(job["company_id"]))
                    .eq("created_by", str(current_user["id"]))
                    .maybe_single()
                    .execute()
                )
                if company_result.data is None:
                    raise ATSNotFoundError("Application not found")

            resume = None
            if load_resume:
                resume_result = (
                    self.database.table("resumes")
                    .select(RESUME_COLUMNS)
                    .eq("id", str(application["resume_id"]))
                    .maybe_single()
                    .execute()
                )
                resume = resume_result.data
                if resume is None or str(resume["candidate_id"]) != str(application["candidate_id"]):
                    raise ATSNotFoundError("Application resume not found")
            return application, resume, job
        except (ATSForbiddenError, ATSNotFoundError):
            raise
        except Exception:
            raise ATSProcessingError("Could not validate application relationships") from None

    def _download_resume(self, file_url: str, candidate_id: str) -> bytes:
        object_path = _storage_object_path(file_url, get_settings().STORAGE_BUCKET)
        if not object_path.startswith(f"{candidate_id}/"):
            raise ATSProcessingError("Resume storage path does not match the application candidate")
        try:
            data = self.database.storage.from_(get_settings().STORAGE_BUCKET).download(object_path)
        except Exception:
            raise ATSProcessingError("Could not retrieve resume from storage") from None
        if not isinstance(data, bytes):
            raise ATSProcessingError("Stored resume content is invalid")
        return data


def _storage_object_path(file_url: str, bucket: str) -> str:
    path = unquote(urlsplit(file_url).path).lstrip("/")
    marker = f"storage/v1/object/{bucket}/"
    if marker in path:
        return path.split(marker, 1)[1]
    if path.startswith(f"{bucket}/"):
        return path[len(bucket) + 1 :]
    raise ValueError("Resume storage URL does not point to the configured bucket")


def _ground_information(information: ResumeInformation, resume_text: str) -> ResumeInformation:
    source = _normalize_claim(resume_text)
    return ResumeInformation(
        skills=[item for item in information.skills if _claim_is_grounded(item, source)],
        education=[item for item in information.education if _claim_is_grounded(item, source)],
        experience=information.experience if _claim_is_grounded(information.experience, source) else "",
        projects=[item for item in information.projects if _claim_is_grounded(item, source)],
    )


def _claim_is_grounded(claim: str, normalized_source: str) -> bool:
    normalized_claim = _normalize_claim(claim)
    return not normalized_claim or normalized_claim in normalized_source


def _normalize_claim(text: str) -> str:
    return re.sub(r"[^a-z0-9+#.]+", " ", text.lower()).strip()


def _build_job_description(job: dict[str, Any]) -> str:
    return "\n".join(
        part
        for part in (
            job.get("title", ""),
            job.get("description", ""),
            "Required skills: " + ", ".join(job.get("required_skills") or []),
            "Required experience: " + (job.get("required_experience") or ""),
        )
        if part
    )


def _match_required_skills(required_skills: list[str], extracted_skills: list[str]) -> tuple[list[str], list[str]]:
    extracted = {skill.casefold().strip() for skill in extracted_skills}
    matching = [skill for skill in required_skills if skill.casefold().strip() in extracted]
    missing = [skill for skill in required_skills if skill.casefold().strip() not in extracted]
    return matching, missing


def _build_explanation(
    score: dict[str, Any],
    matching_skills: list[str],
    missing_skills: list[str],
    information: ResumeInformation,
    job_description: str,
) -> str:
    explanation = (
        f"ATS score {score['score']:.2f}/100 is calculated from 60% semantic similarity "
        f"({score['semantic']:.2f}) and 40% keyword/bigram overlap ({score['keyword']:.2f})."
    )
    if matching_skills:
        explanation += " Matching required skills: " + ", ".join(matching_skills) + "."
    if missing_skills:
        explanation += " Required skills not found in extracted resume information: " + ", ".join(missing_skills) + "."
    if information.experience and _has_job_overlap(information.experience, job_description):
        excerpt = information.experience[:240].rstrip()
        explanation += f" Relevant experience evidence: {excerpt}."
    relevant_projects = [
        project for project in information.projects if _has_job_overlap(project, job_description)
    ]
    if relevant_projects:
        excerpts = "; ".join(project[:120].rstrip() for project in relevant_projects[:2])
        explanation += f" Project excerpts: {excerpts}."
    return explanation


def _has_job_overlap(text: str, job_description: str) -> bool:
    ignored_terms = {"and", "the", "with", "for", "from", "that", "this", "have", "has"}
    evidence_terms = set(re.findall(r"[a-z0-9+#.]{3,}", text.lower())) - ignored_terms
    job_terms = set(re.findall(r"[a-z0-9+#.]{3,}", job_description.lower())) - ignored_terms
    return bool(evidence_terms & job_terms)