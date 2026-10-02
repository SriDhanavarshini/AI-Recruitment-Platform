from fastapi import APIRouter, HTTPException, status

from app.services.ai_service import ai_provider

router = APIRouter(prefix="/interviews", tags=["interviews"])

interviews_db: dict[int, dict] = {}


@router.get("/categories")
def list_categories():
    return ["TECHNICAL", "DOMAIN", "HR"]


@router.post("/{interview_id}/question")
def generate_question(interview_id: int, payload: dict):
    try:
        question = ai_provider.generate_interview_question(payload.get("category", "TECHNICAL"), payload.get("job_context", {}))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    interviews_db.setdefault(interview_id, {})
    interviews_db[interview_id]["question"] = question
    return question


@router.post("/{interview_id}/evaluate")
def evaluate_answer(interview_id: int, payload: dict):
    try:
        evaluation = ai_provider.evaluate_interview_answer(
            payload.get("question", ""),
            payload.get("answer", ""),
            payload.get("category", "TECHNICAL"),
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return {"interview_id": interview_id, "result": evaluation}
