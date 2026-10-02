from fastapi import APIRouter

from app.schemas.schemas import InterviewReportOut

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/pipeline")
def pipeline_report():
    return {
        "stages": [
            "APPLIED",
            "ATS_SHORTLISTED",
            "ASSESSMENT_PENDING",
            "ASSESSMENT_PASSED",
            "AI_INTERVIEW_PENDING",
            "AI_INTERVIEW_COMPLETED",
            "SELECTED",
        ]
    }


@router.get("/interviews/{interview_id}", response_model=InterviewReportOut)
def get_interview_report(interview_id: int):
    return {
        "id": 1,
        "interview_id": interview_id,
        "technical_score": 88,
        "domain_score": 85,
        "communication_score": 90,
        "relevance_score": 87,
        "overall_score": 88,
        "strengths": ["Strong domain knowledge", "Clear communication"],
        "areas_for_improvement": ["Deeper explanation of architecture decisions"],
        "question_evaluations": [{"question": "Explain your design decisions", "score": 8.8}],
    }
