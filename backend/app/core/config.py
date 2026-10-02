from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Recruitment Platform"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    database_url: str = "postgresql://postgres:postgres@localhost:5432/recruitment_db"
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    AI_PROVIDER: str = "gemini"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-1.5-flash"
    JUDGE0_API_URL: str = ""
    JUDGE0_API_KEY: str = ""
    JUDGE0_HOST: str = ""
    CORS_ORIGINS: str = "http://localhost:5173"
    STORAGE_BUCKET: str = "resumes"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
    )

    @property
    def app_name(self) -> str:
        return self.APP_NAME

    @property
    def environment(self) -> str:
        return self.ENVIRONMENT

    @property
    def backend_url(self) -> str:
        return self.BACKEND_URL

    @property
    def frontend_url(self) -> str:
        return self.FRONTEND_URL

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY

    @property
    def algorithm(self) -> str:
        return self.ALGORITHM

    @property
    def access_token_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def supabase_url(self) -> str:
        return self.SUPABASE_URL

    @property
    def supabase_anon_key(self) -> str:
        return self.SUPABASE_ANON_KEY

    @property
    def supabase_service_role_key(self) -> str:
        return self.SUPABASE_SERVICE_ROLE_KEY

    @property
    def ai_provider(self) -> str:
        return self.AI_PROVIDER

    @property
    def ai_api_key(self) -> str:
        return self.AI_API_KEY

    @property
    def ai_model(self) -> str:
        return self.AI_MODEL

    @property
    def judge0_api_url(self) -> str:
        return self.JUDGE0_API_URL

    @property
    def judge0_api_key(self) -> str:
        return self.JUDGE0_API_KEY

    @property
    def judge0_host(self) -> str:
        return self.JUDGE0_HOST

    @property
    def cors_origins(self) -> str:
        return self.CORS_ORIGINS


settings = Settings()


def get_settings() -> Settings:
    return settings
