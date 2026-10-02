from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_candidate_user, require_hr_user
from app.core.supabase import supabase
from app.schemas.schemas import JobCreate, JobOut, JobStatusUpdate, JobUpdate, OpenJobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])

JOB_COLUMNS = (
    "id, company_id, title, description, required_skills, required_experience, "
    "location, employment_type, status, created_at, updated_at"
)


@router.get("", response_model=list[JobOut])
def list_jobs(current_user: dict[str, Any] = Depends(require_hr_user)):
    try:
        company_result = (
            supabase.table("companies")
            .select("id")
            .eq("created_by", str(current_user["id"]))
            .execute()
        )
        company_ids = [company["id"] for company in company_result.data or []]
        if not company_ids:
            return []

        result = (
            supabase.table("jobs")
            .select(JOB_COLUMNS)
            .in_("company_id", company_ids)
            .order("created_at", desc=True)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not retrieve jobs",
        ) from None
    return result.data or []


@router.post("", response_model=JobOut)
def create_job(
    payload: JobCreate,
    current_user: dict[str, Any] = Depends(require_hr_user),
):
    try:
        company = _get_owned_company(payload.company_id, current_user["id"])
        if company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        result = (
            supabase.table("jobs")
            .insert(payload.model_dump(mode="json"))
            .select(JOB_COLUMNS)
            .single()
            .execute()
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create job",
        ) from None
    return result.data


@router.get("/open", response_model=list[OpenJobOut])
def list_open_jobs(current_user: dict[str, Any] = Depends(require_candidate_user)):
    try:
        result = (
            supabase.table("jobs")
            .select(
                "id, title, description, required_skills, required_experience, "
                "location, employment_type, status, created_at"
            )
            .eq("status", "OPEN")
            .order("created_at", desc=True)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not retrieve open jobs",
        ) from None
    return result.data or []


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: UUID, current_user: dict[str, Any] = Depends(require_hr_user)):
    try:
        return _get_owned_job_or_404(job_id, current_user["id"])
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not retrieve job",
        ) from None


@router.put("/{job_id}", response_model=JobOut)
def update_job(
    job_id: UUID,
    payload: JobUpdate,
    current_user: dict[str, Any] = Depends(require_hr_user),
):
    try:
        job = _get_owned_job_or_404(job_id, current_user["id"])
        changes = payload.model_dump(exclude_unset=True, mode="json")
        target_company_id = UUID(changes["company_id"]) if "company_id" in changes else UUID(str(job["company_id"]))
        if target_company_id != UUID(str(job["company_id"])):
            company = _get_owned_company(target_company_id, current_user["id"])
            if company is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        changes["updated_at"] = _now()
        result = (
            supabase.table("jobs")
            .update(changes)
            .eq("id", str(job_id))
            .eq("company_id", str(job["company_id"]))
            .select(JOB_COLUMNS)
            .maybe_single()
            .execute()
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not update job",
        ) from None
    if result.data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return result.data


@router.patch("/{job_id}/status", response_model=JobOut)
def update_job_status(
    job_id: UUID,
    payload: JobStatusUpdate,
    current_user: dict[str, Any] = Depends(require_hr_user),
):
    try:
        job = _get_owned_job_or_404(job_id, current_user["id"])
        result = (
            supabase.table("jobs")
            .update({"status": payload.status, "updated_at": _now()})
            .eq("id", str(job_id))
            .eq("company_id", str(job["company_id"]))
            .select(JOB_COLUMNS)
            .maybe_single()
            .execute()
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not update job status",
        ) from None
    if result.data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return result.data


def _get_owned_company(company_id: UUID, user_id: Any):
    result = (
        supabase.table("companies")
        .select("id")
        .eq("id", str(company_id))
        .eq("created_by", str(user_id))
        .maybe_single()
        .execute()
    )
    return result.data


def _get_owned_job_or_404(job_id: UUID, user_id: Any) -> dict[str, Any]:
    result = (
        supabase.table("jobs")
        .select(JOB_COLUMNS)
        .eq("id", str(job_id))
        .maybe_single()
        .execute()
    )
    if result.data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if _get_owned_company(UUID(str(result.data["company_id"])), user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return result.data


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
