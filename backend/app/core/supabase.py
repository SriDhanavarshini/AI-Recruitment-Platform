from supabase import Client, create_client

from app.core.config import settings


if not settings.SUPABASE_URL.strip():
    raise RuntimeError(
        "Missing required Supabase configuration: SUPABASE_URL. "
        "Set it in backend/.env or the environment."
    )

if not settings.SUPABASE_SERVICE_ROLE_KEY.strip():
    raise RuntimeError(
        "Missing required Supabase configuration: SUPABASE_SERVICE_ROLE_KEY. "
        "Set it in backend/.env or the environment."
    )

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY,
)
