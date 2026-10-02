from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_candidate_user
from app.core.supabase import supabase
from app.schemas.schemas import ApplicationCreate, ApplicationOut
from app.services.reapplication_service import ReapplicationRestrictionService

router = APIRouter(prefix="/applications", tags=["applications"])
APPLICATION_COLUMNS = "id, candidate_id, job_id, resume_id, status, applied_at"
JOB_SUMMARY_COLUMNS = (
    "id, title, description, required_skills, required_experience, location, "
    "employment_type, status"
)



@router.get("", response_model=list[ApplicationOut])
def list_applications(current_user: dict[str, Any] = Depends(require_candidate_user)):
    try:
        result = (
            supabase.table("applications")
            .select(APPLICATION_COLUMNS)
            .eq("candidate_id", str(current_user["id"]))
            .order("applied_at", desc=True)
            .execute()
        )
        applications = result.data or []
        return _include_job_summaries(applications)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not retrieve applications",
        ) from None


@router.post("", response_model=ApplicationOut)
def create_application(
    payload: ApplicationCreate,
    current_user: dict[str, Any] = Depends(require_candidate_user),
):
    candidate_id = str(current_user["id"])
    try:
        resume_result = (
            supabase.table("resumes")
            .select("id")
            .eq("id", str(payload.resume_id))
            .eq("candidate_id", candidate_id)
            .maybe_single()
            .execute()
        )
        if resume_result.data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

        job_result = (
            supabase.table("jobs")
            .select("id, status")
            .eq("id", str(payload.job_id))
            .maybe_single()
            .execute()
        )
        if job_result.data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        if job_result.data["status"] != "OPEN":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is not open for applications")

        existing_result = (
            supabase.table("applications")
            .select(APPLICATION_COLUMNS)
            .eq("candidate_id", candidate_id)
            .eq("job_id", str(payload.job_id))
            .maybe_single()
            .execute()
        )
        existing = existing_result.data
        if existing is not None:
            if existing["status"] != "NOT_SELECTED":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An application already exists for this job",
                )
            rejection = _get_latest_rejection(existing["id"])
            if rejection is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Reapplication is blocked because the rejection date is unavailable",
                )
            rejection_date = _parse_timestamp(rejection["changed_at"]).date()
            eligible_date = ReapplicationRestrictionService.calculate_eligible_reapply_date(rejection_date)
            if datetime.now(timezone.utc).date() < eligible_date:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "Six months must pass after rejection before reapplying",
                        "eligible_date": eligible_date.isoformat(),
                    },
                )

            result = (
                supabase.table("applications")
                .update({
                    "resume_id": str(payload.resume_id),
                    "status": "APPLIED",
                    "applied_at": datetime.now(timezone.utc).isoformat(),
                })
                .eq("id", str(existing["id"]))
                .eq("candidate_id", candidate_id)
                .select(APPLICATION_COLUMNS)
                .single()
                .execute()
            )
        else:
            result = (
                supabase.table("applications")
                .insert({
                    "candidate_id": candidate_id,
                    "job_id": str(payload.job_id),
                    "resume_id": str(payload.resume_id),
                    "status": "APPLIED",
                })
                .select(APPLICATION_COLUMNS)
                .single()
                .execute()
            )
    except HTTPException:
        raise
    except Exception as error:
        if _is_unique_violation(error):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An application already exists for this job",
            ) from None
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create application",
        ) from None
    return _include_job_summaries([result.data])[0]


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: UUID,
    current_user: dict[str, Any] = Depends(require_candidate_user),
):
    try:
        result = (
            supabase.table("applications")
            .select(APPLICATION_COLUMNS)
            .eq("id", str(application_id))
            .eq("candidate_id", str(current_user["id"]))
            .maybe_single()
            .execute()
        )
        if result.data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        return _include_job_summaries([result.data])[0]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not retrieve application",
        ) from None


def _include_job_summaries(applications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    job_ids = list({str(application["job_id"]) for application in applications})
    if not job_ids:
        return []
    result = supabase.table("jobs").select(JOB_SUMMARY_COLUMNS).in_("id", job_ids).execute()
    jobs = {str(job["id"]): job for job in result.data or []}
    return [
        {**application, "job": jobs.get(str(application["job_id"]))}
        for application in applications
    ]


def _get_latest_rejection(application_id: str) -> dict[str, Any] | None:
    result = (
        supabase.table("candidate_status_history")
        .select("changed_at")
        .eq("application_id", str(application_id))
        .eq("new_status", "NOT_SELECTED")
        .order("changed_at", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    return result.data


def _parse_timestamp(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _is_unique_violation(error: Exception) -> bool:
    return getattr(error, "code", None) == "23505" or "duplicate key value violates unique constraint" in str(error).lower()


@router.post("/{application_id}/decision")
def update_application_decision(application_id: UUID, decision: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Application decisions are not available yet")
