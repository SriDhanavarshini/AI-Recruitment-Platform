from fastapi import APIRouter, HTTPException, status

from app.schemas.schemas import CodingSubmissionCreate, CodingSubmissionOut

router = APIRouter(prefix="/coding", tags=["coding"])

submissions_db: dict[int, dict] = {}


@router.get("/problems")
def list_problems():
    return [
        {
            "id": 1,
            "title": "Two Sum",
            "statement": "Given an array of integers, return indices of two numbers that add to a target.",
            "supported_languages": ["Python", "Java", "C++"],
        }
    ]


@router.post("/submit", response_model=CodingSubmissionOut)
def submit_code(payload: CodingSubmissionCreate):
    if not payload.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code cannot be empty")
    submission_id = len(submissions_db) + 1
    submission = {
        "id": submission_id,
        "passed_tests": 2,
        "failed_tests": 0,
        "execution_time_ms": 120,
        "memory_kb": 256000,
        "score": 100.0,
        **payload.model_dump(),
    }
    submissions_db[submission_id] = submission
    return submission
