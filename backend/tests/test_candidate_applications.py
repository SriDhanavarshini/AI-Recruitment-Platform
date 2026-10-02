from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.api.routers import applications, jobs, resumes
from app.main import app
from app.services.reapplication_service import ReapplicationRestrictionService

client = TestClient(app)
CANDIDATE_ID = "11111111-1111-4111-8111-111111111111"
OTHER_CANDIDATE_ID = "22222222-2222-4222-8222-222222222222"
OPEN_JOB_ID = "33333333-3333-4333-8333-333333333333"
SECOND_OPEN_JOB_ID = "44444444-4444-4444-8444-444444444444"
CLOSED_JOB_ID = "55555555-5555-4555-8555-555555555555"
OWN_RESUME_ID = "66666666-6666-4666-8666-666666666666"
OTHER_RESUME_ID = "77777777-7777-4777-8777-777777777777"
OWN_APPLICATION_ID = "88888888-8888-4888-8888-888888888888"
OTHER_APPLICATION_ID = "99999999-9999-4999-8999-999999999999"


def _job(job_id, title, status="OPEN"):
    return {
        "id": job_id,
        "company_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "title": title,
        "description": "Build reliable services",
        "required_skills": ["Python"],
        "required_experience": "3+ years",
        "location": "Remote",
        "employment_type": "FULL_TIME",
        "status": status,
        "created_at": "2026-10-01T12:00:00+00:00",
        "updated_at": "2026-10-01T12:00:00+00:00",
    }


def _application(application_id, candidate_id, job_id, resume_id, status="APPLIED", applied_at=None):
    return {
        "id": application_id,
        "candidate_id": candidate_id,
        "job_id": job_id,
        "resume_id": resume_id,
        "status": status,
        "applied_at": applied_at or "2026-10-01T12:00:00+00:00",
    }


class UniqueViolation(Exception):
    code = "23505"


class FakeQuery:
    def __init__(self, database, table_name):
        self.database = database
        self.table_name = table_name
        self.action = "select"
        self.payload = None
        self.filters = {}
        self.in_filters = {}
        self.ordering = None
        self.limit_value = None
        self.single_result = False

    def select(self, _columns):
        return self

    def insert(self, payload):
        self.action = "insert"
        self.payload = dict(payload)
        return self

    def update(self, payload):
        self.action = "update"
        self.payload = dict(payload)
        return self

    def eq(self, column, value):
        self.filters[column] = str(value)
        return self

    def in_(self, column, values):
        self.in_filters[column] = {str(value) for value in values}
        return self

    def order(self, column, desc=False):
        self.ordering = (column, desc)
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def maybe_single(self):
        self.single_result = True
        return self

    def single(self):
        self.single_result = True
        return self

    def execute(self):
        rows = self.database.tables[self.table_name]
        if self.action == "insert":
            if self.table_name == "applications" and any(
                row["candidate_id"] == self.payload["candidate_id"]
                and row["job_id"] == self.payload["job_id"]
                for row in rows
            ):
                raise UniqueViolation("duplicate key value violates unique constraint")
            self.database.insert_payloads.append((self.table_name, dict(self.payload)))
            if self.table_name == "resumes":
                row = {
                    **self.payload,
                    "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                    "uploaded_at": "2026-10-02T12:00:00+00:00",
                }
            else:
                row = {
                    **self.payload,
                    "id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
                    "applied_at": "2026-10-02T12:00:00+00:00",
                }
            rows.append(row)
            return SimpleNamespace(data=row)

        matched = [
            row
            for row in rows
            if all(str(row.get(key)) == value for key, value in self.filters.items())
            and all(str(row.get(key)) in values for key, values in self.in_filters.items())
        ]
        if self.ordering:
            key, desc = self.ordering
            matched.sort(key=lambda row: row.get(key) or "", reverse=desc)
        if self.limit_value is not None:
            matched = matched[: self.limit_value]
        if self.action == "update":
            for row in matched:
                row.update(self.payload)
        if self.single_result:
            return SimpleNamespace(data=matched[0] if matched else None)
        return SimpleNamespace(data=matched)


class FakeStorageBucket:
    def __init__(self, database):
        self.database = database

    def upload(self, path, contents, file_options):
        self.database.uploads[path] = (contents, file_options)
        return {"path": path}

    def remove(self, paths):
        for path in paths:
            self.database.uploads.pop(path, None)


class FakeStorage:
    def __init__(self, database):
        self.database = database

    def from_(self, _bucket):
        return FakeStorageBucket(self.database)


class FakeSupabase:
    def __init__(self):
        self.tables = {
            "jobs": [
                _job(OPEN_JOB_ID, "Backend Engineer"),
                _job(SECOND_OPEN_JOB_ID, "Data Engineer"),
                _job(CLOSED_JOB_ID, "Closed Role", "CLOSED"),
            ],
            "resumes": [
                {
                    "id": OWN_RESUME_ID,
                    "candidate_id": CANDIDATE_ID,
                    "file_name": "resume.pdf",
                    "file_url": "private/resume.pdf",
                    "uploaded_at": "2026-10-01T12:00:00+00:00",
                },
                {
                    "id": OTHER_RESUME_ID,
                    "candidate_id": OTHER_CANDIDATE_ID,
                    "file_name": "other.pdf",
                    "file_url": "private/other.pdf",
                    "uploaded_at": "2026-10-01T12:00:00+00:00",
                },
            ],
            "applications": [
                _application(OWN_APPLICATION_ID, CANDIDATE_ID, OPEN_JOB_ID, OWN_RESUME_ID),
                _application(OTHER_APPLICATION_ID, OTHER_CANDIDATE_ID, SECOND_OPEN_JOB_ID, OTHER_RESUME_ID),
            ],
            "candidate_status_history": [],
        }
        self.insert_payloads = []
        self.uploads = {}
        self.storage = FakeStorage(self)

    def table(self, table_name):
        return FakeQuery(self, table_name)


def _as_candidate(monkeypatch, role="CANDIDATE", candidate_id=CANDIDATE_ID):
    database = FakeSupabase()
    for module in (applications, jobs, resumes):
        monkeypatch.setattr(module, "supabase", database)
    app.dependency_overrides[get_current_user] = lambda: {
        "id": candidate_id,
        "name": "Test Person",
        "role": role,
        "auth_id": candidate_id,
    }
    return database


def _clear_auth_override():
    app.dependency_overrides.pop(get_current_user, None)


def test_candidate_endpoints_require_authentication():
    assert client.get("/jobs/open").status_code == 401
    assert client.get("/applications").status_code == 401
    assert client.get(f"/applications/{OWN_APPLICATION_ID}").status_code == 401
    assert client.post("/applications", json={"job_id": OPEN_JOB_ID, "resume_id": OWN_RESUME_ID}).status_code == 401
    assert client.post("/resumes", files={"file": ("resume.pdf", b"pdf data", "application/pdf")}).status_code == 401


def test_hr_cannot_access_candidate_endpoints(monkeypatch):
    _as_candidate(monkeypatch, role="HR")
    try:
        open_jobs = client.get("/jobs/open")
        application_list = client.get("/applications")
        resume = client.post("/resumes", files={"file": ("resume.pdf", b"pdf data", "application/pdf")})
    finally:
        _clear_auth_override()
    assert open_jobs.status_code == 403
    assert application_list.status_code == 403
    assert resume.status_code == 403


def test_candidate_sees_open_jobs_without_company_details(monkeypatch):
    _as_candidate(monkeypatch)
    try:
        response = client.get("/jobs/open")
    finally:
        _clear_auth_override()
    assert response.status_code == 200
    assert {job["id"] for job in response.json()} == {OPEN_JOB_ID, SECOND_OPEN_JOB_ID}
    assert all(job["status"] == "OPEN" and "company_id" not in job for job in response.json())


def test_candidate_uploads_resume_to_private_candidate_path(monkeypatch):
    database = _as_candidate(monkeypatch)
    try:
        response = client.post(
            "/resumes",
            files={"file": ("my-resume.pdf", b"pdf bytes", "application/pdf")},
        )
    finally:
        _clear_auth_override()
    assert response.status_code == 201
    assert response.json()["candidate_id"] == CANDIDATE_ID
    assert response.json()["file_name"] == "my-resume.pdf"
    assert len(database.uploads) == 1
    storage_path, (content, options) = next(iter(database.uploads.items()))
    assert storage_path.startswith(f"{CANDIDATE_ID}/")
    assert content == b"pdf bytes"
    assert options["upsert"] == "false"
    table_name, payload = database.insert_payloads[0]
    assert table_name == "resumes"
    assert payload["candidate_id"] == CANDIDATE_ID
    assert payload["file_name"] == "my-resume.pdf"
    assert set(payload) == {"candidate_id", "file_name", "file_url"}


def test_candidate_cannot_apply_to_closed_job(monkeypatch):
    _as_candidate(monkeypatch)
    try:
        response = client.post(
            "/applications",
            json={"job_id": CLOSED_JOB_ID, "resume_id": OWN_RESUME_ID},
        )
    finally:
        _clear_auth_override()
    assert response.status_code == 409
    assert response.json()["detail"] == "Job is not open for applications"


def test_candidate_can_apply_and_duplicate_is_clean_conflict(monkeypatch):
    database = _as_candidate(monkeypatch)
    try:
        first = client.post(
            "/applications",
            json={"job_id": SECOND_OPEN_JOB_ID, "resume_id": OWN_RESUME_ID},
        )
        duplicate = client.post(
            "/applications",
            json={"job_id": SECOND_OPEN_JOB_ID, "resume_id": OWN_RESUME_ID},
        )
    finally:
        _clear_auth_override()
    assert first.status_code == 200
    assert first.json()["status"] == "APPLIED"
    assert first.json()["job"]["id"] == SECOND_OPEN_JOB_ID
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "An application already exists for this job"
    app_inserts = [payload for table, payload in database.insert_payloads if table == "applications"]
    assert len(app_inserts) == 1
    assert app_inserts[0] == {
        "candidate_id": CANDIDATE_ID,
        "job_id": SECOND_OPEN_JOB_ID,
        "resume_id": OWN_RESUME_ID,
        "status": "APPLIED",
    }


def test_candidate_cannot_apply_with_another_candidates_resume(monkeypatch):
    database = _as_candidate(monkeypatch)
    try:
        response = client.post(
            "/applications",
            json={"job_id": SECOND_OPEN_JOB_ID, "resume_id": OTHER_RESUME_ID},
        )
    finally:
        _clear_auth_override()
    assert response.status_code == 404
    assert not [payload for table, payload in database.insert_payloads if table == "applications"]


def test_candidate_lists_and_reads_only_their_applications(monkeypatch):
    _as_candidate(monkeypatch)
    try:
        listed = client.get("/applications")
        own = client.get(f"/applications/{OWN_APPLICATION_ID}")
        other = client.get(f"/applications/{OTHER_APPLICATION_ID}")
    finally:
        _clear_auth_override()
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [OWN_APPLICATION_ID]
    assert listed.json()[0]["job"]["title"] == "Backend Engineer"
    assert "candidate_id" not in listed.json()[0]
    assert own.status_code == 200
    assert own.json()["job"]["id"] == OPEN_JOB_ID
    assert other.status_code == 404


def test_six_month_restriction_is_job_specific(monkeypatch):
    database = _as_candidate(monkeypatch)
    database.tables["applications"] = [
        application
        for application in database.tables["applications"]
        if not (application["candidate_id"] == CANDIDATE_ID and application["job_id"] == OPEN_JOB_ID)
    ]
    rejected_at = datetime.now(timezone.utc) - timedelta(days=30)
    rejected_application = _application(
        "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
        CANDIDATE_ID,
        OPEN_JOB_ID,
        OWN_RESUME_ID,
        status="NOT_SELECTED",
    )
    database.tables["applications"].append(rejected_application)
    database.tables["candidate_status_history"].append({
        "application_id": rejected_application["id"],
        "new_status": "NOT_SELECTED",
        "changed_at": rejected_at.isoformat(),
    })
    try:
        blocked = client.post(
            "/applications",
            json={"job_id": OPEN_JOB_ID, "resume_id": OWN_RESUME_ID},
        )
        other_job = client.post(
            "/applications",
            json={"job_id": SECOND_OPEN_JOB_ID, "resume_id": OWN_RESUME_ID},
        )
    finally:
        _clear_auth_override()
    eligible_date = ReapplicationRestrictionService.calculate_eligible_reapply_date(rejected_at.date())
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["eligible_date"] == eligible_date.isoformat()
    assert other_job.status_code == 200


def test_reapplication_after_six_months_reuses_unique_application(monkeypatch):
    database = _as_candidate(monkeypatch)
    database.tables["applications"] = [
        application
        for application in database.tables["applications"]
        if not (application["candidate_id"] == CANDIDATE_ID and application["job_id"] == OPEN_JOB_ID)
    ]
    rejection_date = datetime.now(timezone.utc) - timedelta(days=200)
    rejected_application = _application(
        "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
        CANDIDATE_ID,
        OPEN_JOB_ID,
        OWN_RESUME_ID,
        status="NOT_SELECTED",
    )
    database.tables["applications"].append(rejected_application)
    database.tables["candidate_status_history"].append({
        "application_id": rejected_application["id"],
        "new_status": "NOT_SELECTED",
        "changed_at": rejection_date.isoformat(),
    })
    try:
        response = client.post(
            "/applications",
            json={"job_id": OPEN_JOB_ID, "resume_id": OWN_RESUME_ID},
        )
    finally:
        _clear_auth_override()
    assert response.status_code == 200
    assert response.json()["id"] == rejected_application["id"]
    assert response.json()["status"] == "APPLIED"
    assert len([row for row in database.tables["applications"] if row["job_id"] == OPEN_JOB_ID and row["candidate_id"] == CANDIDATE_ID]) == 1
    assert not [payload for table, payload in database.insert_payloads if table == "applications"]
