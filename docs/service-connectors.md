# Service connector guide

## Supabase

1. Create a Postgres database in Supabase.
2. Copy the project URL and anon/service role keys into `.env`.
3. Point `DATABASE_URL` to the Supabase Postgres instance.
4. Use Supabase Auth for login and role metadata.
5. Use Supabase Storage for uploaded resumes and candidate files.

## AI API provider

Set the following values in `.env`:

- `AI_PROVIDER`
- `AI_API_KEY`
- `AI_MODEL`

The app expects a provider-compatible API surface. The abstract interface in `backend/app/services/ai_service.py` allows you to switch providers cleanly.

## Judge0

Configure:

- `JUDGE0_API_URL`
- `JUDGE0_API_KEY`
- `JUDGE0_HOST`

The judge client is implemented under `backend/app/services/coding_service.py`.

## MediaPipe

The browser integration should load MediaPipe from CDN or package manager and run face detection in the candidate assessment page. The backend receives only event metadata such as `FACE_NOT_DETECTED` and `CAMERA_DISCONNECTED`.
