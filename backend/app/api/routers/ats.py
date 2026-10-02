from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.ats_schemas import ATSProcessResponse
from app.services.ats_pipeline_service import (
    ATSConflictError,
    ATSForbiddenError,
    ATSInputError,
    ATSNotFoundError,
    ATSPipelineService,
    ATSProcessingError,
)
from app.services.ats_service import ATSScoringService

router = APIRouter(prefix="/ats", tags=["ats"])


@router.post("/score")
def score_resume(payload: dict):
    resume = payload.get("resume", {})
    job = payload.get("job", {})
    if not resume or not job:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume and job payload are required")

    result = ATSScoringService.calculate_score(
        extracted_resume={
            "skills": resume.get("skills", []),
            "education": resume.get("education"),
            "projects": resume.get("projects"),
        },
        job_requirements={
            "required_skills": job.get("required_skills", []),
            "required_experience": job.get("required_experience"),
            "education": job.get("education"),
            "keywords": job.get("keywords", []),
        },
    )
    return result


@router.post("/applications/{application_id}/process", response_model=ATSProcessResponse)
def process_application_ats(
    application_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    try:
        return ATSPipelineService().process_application(application_id, current_user)
    except ATSNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from None
    except ATSForbiddenError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from None
    except ATSConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from None
    except ATSInputError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from None
    except ATSProcessingError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from None


@router.get("/applications/{application_id}", response_model=ATSProcessResponse)
def get_application_ats_result(
    application_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    try:
        return ATSPipelineService().get_result(application_id, current_user)
    except ATSNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from None
    except ATSForbiddenError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from None
    except ATSProcessingError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from None
