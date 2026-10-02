from fastapi import APIRouter, HTTPException, status

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
