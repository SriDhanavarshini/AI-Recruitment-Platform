from datetime import date
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.api.routers import companies
from app.api.routers import jobs as jobs_router
from app.services.ats_service import ATSScoringService
from app.services.reapplication_service import ReapplicationRestrictionService

client = TestClient(app)


class FakeCompanyQuery:
    def __init__(self, database):
        self.database = database
        self.filters = {}
        self.payload = None

    def select(self, _columns):
        return self

    def insert(self, payload):
        self.payload = payload
        return self

    def eq(self, column, value):
        self.filters[column] = value
        return self

    def order(self, _column, desc=False):
        return self

    def single(self):
        return self

    def maybe_single(self):
        return self

    def execute(self):
        if self.payload is not None:
            row = {
                **self.payload,
                "id": 41,
                "created_at": "2026-10-02T12:00:00+00:00",
            }
            self.database.rows.append(row)
            return SimpleNamespace(data=row)

        rows = [
            row
            for row in self.database.rows
            if all(row.get(key) == value for key, value in self.filters.items())
        ]
        return SimpleNamespace(data=rows)


class FakeCompanyDatabase:
    def __init__(self):
        self.rows = [
            {
                "id": 40,
                "name": "Other HR Company",
                "created_by": 8,
                "created_at": "2026-10-01T12:00:00+00:00",
            }
        ]

    def table(self, _table_name):
        return FakeCompanyQuery(self)


def test_companies_require_authentication():
    response = client.get("/companies")
    assert response.status_code == 401


def test_candidate_cannot_create_company():
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 12,
        "name": "Candidate",
        "role": "CANDIDATE",
        "auth_id": "candidate-auth-id",
    }
    try:
        response = client.post("/companies", json={"name": "Blocked Company"})
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


def test_hr_can_create_and_list_only_their_companies(monkeypatch):
    database = FakeCompanyDatabase()
    monkeypatch.setattr(companies, "supabase", database)
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 7,
        "name": "HR User",
        "role": "HR",
        "auth_id": "different-auth-id",
    }
    try:
        created = client.post("/companies", json={"name": "Acme"})
        listed = client.get("/companies")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert created.status_code == 200
    assert created.json() == {
        "id": 41,
        "name": "Acme",
        "created_by": 7,
        "created_at": "2026-10-02T12:00:00Z",
    }
    assert listed.status_code == 200
    assert [company["name"] for company in listed.json()] == ["Acme"]
    assert len(database.rows) == 2
    assert database.rows[-1] == {"name": "Acme", "created_by": 7, "id": 41, "created_at": "2026-10-02T12:00:00+00:00"}


def test_jobs_endpoint_requires_authentication():
    response = client.get("/jobs")
    assert response.status_code == 401


USER_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
OWN_COMPANY_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
OTHER_COMPANY_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
OWN_JOB_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
OTHER_JOB_ID = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"


def job_record(job_id, company_id, title="Engineer", status="OPEN"):
    return {
        "id": job_id,
        "company_id": company_id,
        "title": title,
        "description": "Build useful software",
        "required_skills": ["Python"],
        "required_experience": "3+ years",
        "location": "Remote",
        "employment_type": "FULL_TIME",
        "status": status,
        "created_at": "2026-10-01T12:00:00+00:00",
        "updated_at": "2026-10-01T12:00:00+00:00",
    }


class FakeJobsQuery:
    def __init__(self, database, table):
        self.database = database
        self.table_name = table
        self.filters = {}
        self.in_filters = {}
        self.action = "select"
        self.payload = None
        self.single_result = False

    def select(self, _columns):
        return self

    def insert(self, payload):
        self.action = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.action = "update"
        self.payload = payload
        return self

    def eq(self, column, value):
        self.filters[column] = value
        return self

    def in_(self, column, values):
        self.in_filters[column] = values
        return self

    def order(self, _column, desc=False):
        return self

    def single(self):
        self.single_result = True
        return self

    def maybe_single(self):
        self.single_result = True
        return self

    def execute(self):
        rows = self.database.tables[self.table_name]
        if self.action == "insert":
            self.database.insert_payloads.append(dict(self.payload))
            row = {
                **self.payload,
                "id": "ffffffff-ffff-4fff-8fff-ffffffffffff",
                "status": "OPEN",
                "created_at": "2026-10-02T12:00:00+00:00",
                "updated_at": "2026-10-02T12:00:00+00:00",
            }
            rows.append(row)
            return SimpleNamespace(data=row)

        matched = [
            row
            for row in rows
            if all(str(row.get(key)) == str(value) for key, value in self.filters.items())
            and all(str(row.get(key)) in {str(value) for value in values} for key, values in self.in_filters.items())
        ]
        if self.action == "update":
            for row in matched:
                row.update(self.payload)
        if self.single_result:
            return SimpleNamespace(data=matched[0] if matched else None)
        return SimpleNamespace(data=matched)


class FakeJobsDatabase:
    def __init__(self):
        self.insert_payloads = []
        self.tables = {
            "companies": [
                {"id": OWN_COMPANY_ID, "created_by": USER_ID},
                {"id": OTHER_COMPANY_ID, "created_by": "99999999-9999-4999-8999-999999999999"},
            ],
            "jobs": [
                job_record(OWN_JOB_ID, OWN_COMPANY_ID),
                job_record(OTHER_JOB_ID, OTHER_COMPANY_ID, title="Private role"),
            ],
        }

    def table(self, table_name):
        return FakeJobsQuery(self, table_name)


def use_job_database(monkeypatch, role="HR", user_id=USER_ID):
    database = FakeJobsDatabase()
    monkeypatch.setattr(jobs_router, "supabase", database)
    app.dependency_overrides[get_current_user] = lambda: {
        "id": user_id,
        "name": "Test User",
        "role": role,
        "auth_id": user_id,
    }
    return database


def test_candidate_cannot_access_jobs(monkeypatch):
    use_job_database(monkeypatch, role="CANDIDATE")
    try:
        response = client.get("/jobs")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert response.status_code == 403


def test_hr_creates_job_for_owned_company_with_database_defaults(monkeypatch):
    database = use_job_database(monkeypatch)
    try:
        response = client.post(
            "/jobs",
            json={
                "company_id": OWN_COMPANY_ID,
                "title": "Platform Engineer",
                "description": "Build platform services",
                "required_skills": ["Python", "SQL"],
                "required_experience": "4+ years",
                "location": "Remote",
                "employment_type": "FULL_TIME",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert response.status_code == 200
    assert response.json()["status"] == "OPEN"
    assert response.json()["id"] == "ffffffff-ffff-4fff-8fff-ffffffffffff"
    inserted = database.tables["jobs"][-1]
    assert inserted["company_id"] == OWN_COMPANY_ID
    assert set(database.insert_payloads[0]) == {
        "company_id", "title", "description", "required_skills", "required_experience",
        "location", "employment_type",
    }
    assert set(inserted) == {
        "company_id", "title", "description", "required_skills", "required_experience",
        "location", "employment_type", "id", "status", "created_at", "updated_at",
    }


def test_hr_lists_only_jobs_for_owned_companies(monkeypatch):
    use_job_database(monkeypatch)
    try:
        response = client.get("/jobs")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert response.status_code == 200
    assert [job["id"] for job in response.json()] == [OWN_JOB_ID]


def test_hr_can_get_own_job_but_not_another_hr_job(monkeypatch):
    use_job_database(monkeypatch)
    try:
        own = client.get(f"/jobs/{OWN_JOB_ID}")
        other = client.get(f"/jobs/{OTHER_JOB_ID}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert own.status_code == 200
    assert other.status_code == 404


def test_hr_can_update_own_job(monkeypatch):
    database = use_job_database(monkeypatch)
    try:
        response = client.put(f"/jobs/{OWN_JOB_ID}", json={"title": "Senior Engineer"})
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert response.status_code == 200
    assert response.json()["title"] == "Senior Engineer"
    assert database.tables["jobs"][0]["updated_at"] != "2026-10-01T12:00:00+00:00"


def test_hr_can_open_and_close_own_job(monkeypatch):
    database = use_job_database(monkeypatch)
    try:
        closed = client.patch(f"/jobs/{OWN_JOB_ID}/status", json={"status": "CLOSED"})
        reopened = client.patch(f"/jobs/{OWN_JOB_ID}/status", json={"status": "OPEN"})
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert closed.status_code == 200
    assert closed.json()["status"] == "CLOSED"
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "OPEN"
    assert database.tables["jobs"][0]["updated_at"] != "2026-10-01T12:00:00+00:00"


def test_foreign_company_and_job_updates_are_rejected(monkeypatch):
    use_job_database(monkeypatch)
    payload = {"company_id": OTHER_COMPANY_ID, "title": "Blocked", "description": "No access", "employment_type": "FULL_TIME"}
    try:
        create = client.post("/jobs", json=payload)
        update = client.put(f"/jobs/{OWN_JOB_ID}", json={"company_id": OTHER_COMPANY_ID})
        status_update = client.patch(f"/jobs/{OTHER_JOB_ID}/status", json={"status": "CLOSED"})
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert create.status_code == 404
    assert update.status_code == 404
    assert status_update.status_code == 404


def test_invalid_job_fields_are_rejected(monkeypatch):
    use_job_database(monkeypatch)
    try:
        empty_title = client.post("/jobs", json={"company_id": OWN_COMPANY_ID, "title": "  ", "description": "Valid", "employment_type": "FULL_TIME"})
        invalid_skills = client.post("/jobs", json={"company_id": OWN_COMPANY_ID, "title": "Valid", "description": "Valid", "required_skills": "Python", "employment_type": "FULL_TIME"})
        invalid_status = client.patch(f"/jobs/{OWN_JOB_ID}/status", json={"status": "PAUSED"})
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert empty_title.status_code == 422
    assert invalid_skills.status_code == 422
    assert invalid_status.status_code == 422


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
    assert eligible_date == date(2025, 7, 15)
