# AI Recruitment Platform

A modular full-stack recruitment platform built with a FastAPI backend and a Vite React frontend. It is structured for Supabase, external AI APIs, secure code execution via Judge0, and browser-side proctoring with MediaPipe.

## Project structure

```text
recruitment-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── routers/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .venv/
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── node_modules/
├── database/
│   ├── schema.sql
│   └── seed.sql
├── docs/
│   ├── architecture.md
│   └── service-connectors.md
├── .env.example
├── .gitignore
├── README.md
└── .
```

## Setup instructions

### 1. Environment configuration

```bash
cp .env.example .env
```

Update the file with your actual credentials for:

- Supabase PostgreSQL
- Supabase Auth
- Supabase Storage
- AI API provider
- Judge0

### 2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

### 4. Database setup

Use the SQL in `database/schema.sql` with your Supabase/PostgreSQL instance and optionally seed with `database/seed.sql`.

## Environment variables

See `.env.example` for a complete set of placeholders.

## AI service design

The AI layer is abstracted under `backend/app/services/ai_service.py` and uses environment-based configuration. It is designed so a provider can be swapped transparently without changing the rest of the business logic.

## ATS scoring design

ATS logic is calculated in `backend/app/services/ats_service.py` with deterministic weighting. The application never allows the LLM to set the final ATS score arbitrarily.

## Coding execution design

The candidate code is not executed directly on the FastAPI host. Code is submitted to an external sandbox client via `Judge0` in `backend/app/services/coding_service.py`.

## Proctoring design

The frontend uses MediaPipe face detection in the browser. Only event metadata such as `FACE_NOT_DETECTED`, `MULTIPLE_FACES`, and `CAMERA_DISCONNECTED` is transmitted to the backend. No continuous video stream is stored.

## API documentation

FastAPI automatically exposes API docs at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Testing

```bash
cd backend
source .venv/bin/activate
pytest
```

## Notes on external services

This project is intentionally designed to work with cloud services and external APIs; there is no local GPU or local model execution requirement.
