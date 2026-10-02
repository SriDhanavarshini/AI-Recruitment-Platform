from fastapi import APIRouter, HTTPException, status

from app.schemas.schemas import JobCreate, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])

jobs_db: dict[int, dict] = {}


@router.get("", response_model=list[JobOut])
def list_jobs():
    return list(jobs_db.values())


@router.post("", response_model=JobOut)
def create_job(payload: JobCreate):
    job_id = len(jobs_db) + 1
    job = {"id": job_id, **payload.model_dump()}
    jobs_db[job_id] = job
    return job


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int):
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
