from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.services.ats_service import ATSScoringService
from app.services.reapplication_service import ReapplicationRestrictionService

client = TestClient(app)


def test_jobs_endpoint():
    response = client.get("/jobs")
    assert response.status_code == 200


def test_duplicate_application_endpoint_rejected():
    payload = {"candidate_id": 1, "job_id": 1, "resume_id": 1}
    first = client.post("/applications", json=payload)
    second = client.post("/applications", json=payload)
    assert first.status_code == 200
    assert second.status_code == 409


def test_ats_scoring():
    result = ATSScoringService.calculate_score(
        extracted_resume={"skills": ["Python", "FastAPI", "SQL"], "education": "BSc CS", "projects": ["recruitment platform"]},
        job_requirements={"required_skills": ["Python", "FastAPI", "SQL", "React"], "required_experience": "3+ years", "education": "BSc", "keywords": ["API", "database"]},
    )
    assert result["score"] > 0
    assert "missing_skills" in result


def test_reapply_window():
    rejection_date = date(2025, 1, 15)
    eligible_date = ReapplicationRestrictionService.calculate_eligible_reapply_date(rejection_date)
    assert eligible_date == date(2025, 7, 17)
