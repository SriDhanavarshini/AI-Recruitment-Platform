# Architecture guide

## Backend modules

- `app/api`: HTTP routes grouped by feature area.
- `app/core`: environment configuration and security helpers.
- `app/models`: SQLAlchemy models representing the relational schema.
- `app/schemas`: request and response contracts for FastAPI.
- `app/services`: business logic, ATS scoring, AI abstraction, coding execution, assessment scoring.
- `app/repositories`: repository wrappers for common database access patterns.
- `app/utils`: supportive helpers and formatting utilities.

## AI service design

The platform intentionally separates provider integration from business logic. `ExternalAIProvider` implements the abstract `AIProvider` interface, which can be swapped to Gemini, OpenAI, or another compatible provider without changing the rest of the application.

The application does not depend on local GPUs or local model downloads. Each call must use environment-based credentials and an external provider.

## ATS scoring rule

The final ATS decision is never left to the LLM. It must be calculated in code using deterministic criteria. The example weighting in the project is:

- Skills: 40%
- Experience: 25%
- Project relevance: 15%
- Education: 10%
- Keyword relevance: 10%

This is enforced through the `ATSScoringService` in the backend.

## Proctoring rule

The browser-based proctoring layer uses MediaPipe face detection locally in the frontend. It stores only event metadata and timestamps, not webcam recordings.

## Deployment model

- Supabase for Postgres, Auth, and Storage
- AI API provider for LLM calls
- Judge0 for code execution sandbox
- Frontend uses Vite and connects to the backend over environment variables
