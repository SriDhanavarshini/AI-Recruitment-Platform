from fastapi import APIRouter, HTTPException, status

from app.schemas.schemas import AssessmentCreate, AssessmentOut
from app.services.assessment_service import AssessmentScoringService

router = APIRouter(prefix="/assessments", tags=["assessments"])

assessments_db: dict[int, dict] = {}


@router.get("", response_model=list[AssessmentOut])
def list_assessments():
    return list(assessments_db.values())


@router.post("", response_model=AssessmentOut)
def create_assessment(payload: AssessmentCreate):
    assessment_id = len(assessments_db) + 1
    assessment = {"id": assessment_id, **payload.model_dump()}
    assessments_db[assessment_id] = assessment
    return assessment


@router.post("/{assessment_id}/score")
def score_assessment(assessment_id: int, answers: list[dict]):
    assessment = assessments_db.get(assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    score = AssessmentScoringService.score_attempt(answers, total_marks=assessment.get("marks", 100))
    return {"assessment_id": assessment_id, **score}
