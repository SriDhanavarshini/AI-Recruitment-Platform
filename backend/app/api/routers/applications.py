from datetime import date

from fastapi import APIRouter, HTTPException, status

from app.schemas.schemas import ApplicationCreate, ApplicationOut

router = APIRouter(prefix="/applications", tags=["applications"])

applications_db: dict[int, dict] = {}


@router.get("", response_model=list[ApplicationOut])
def list_applications():
    return list(applications_db.values())


@router.post("", response_model=ApplicationOut)
def create_application(payload: ApplicationCreate):
    duplicate = next((app for app in applications_db.values() if app["candidate_id"] == payload.candidate_id and app["job_id"] == payload.job_id), None)
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate application detected for this job")
    application_id = len(applications_db) + 1
    app = {"id": application_id, "status": "APPLIED", "ats_score": 0.0, **payload.model_dump()}
    applications_db[application_id] = app
    return app


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(application_id: int):
    app = applications_db.get(application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return app


@router.post("/{application_id}/decision")
def update_application_decision(application_id: int, decision: str):
    app = applications_db.get(application_id)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    allowed = {"ATS_SHORTLISTED", "ASSESSMENT_PENDING", "SELECTED", "NOT_SELECTED"}
    if decision not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status transition")
    app["status"] = decision
    return {"application_id": application_id, "status": decision}
