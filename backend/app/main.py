from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import (
    applications,
    ats,
    assessments,
    auth,
    coding,
    companies,
    interviews,
    jobs,
    proctoring,
    questions,
    reports,
    resumes,
    users,
)
from app.core.config import get_settings
from app.core.supabase import supabase

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(resumes.router)
app.include_router(ats.router)
app.include_router(assessments.router)
app.include_router(questions.router)
app.include_router(coding.router)
app.include_router(proctoring.router)
app.include_router(interviews.router)
app.include_router(reports.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/health/db")
def database_health_check() -> dict[str, str]:
    try:
        supabase.table("users").select("id").limit(1).execute()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connectivity check failed.",
        ) from None

    return {"database": "connected", "query": "successful"}
