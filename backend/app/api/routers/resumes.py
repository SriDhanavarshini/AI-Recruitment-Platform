from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.api.deps import require_candidate_user
from app.core.config import settings
from app.core.supabase import supabase
from app.schemas.schemas import ResumeUpload

router = APIRouter(prefix="/resumes", tags=["resumes"])
RESUME_COLUMNS = "id, candidate_id, file_name, file_url, uploaded_at"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("", response_model=ResumeUpload, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile,
    current_user: dict[str, Any] = Depends(require_candidate_user),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported resume format")
    file_name = Path(file.filename).name
    extension = Path(file_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported resume format")

    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume file is empty")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Resume file is too large")

    candidate_id = str(current_user["id"])
    storage_path = f"{candidate_id}/{uuid4().hex}{extension}"
    file_url = (
        f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/"
        f"{settings.STORAGE_BUCKET}/{storage_path}"
    )
    try:
        supabase.storage.from_(settings.STORAGE_BUCKET).upload(
            storage_path,
            contents,
            file_options={
                "content-type": file.content_type or "application/octet-stream",
                "upsert": "false",
            },
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not store resume",
        ) from None

    try:
        result = (
            supabase.table("resumes")
            .insert({
                "candidate_id": candidate_id,
                "file_name": file_name,
                "file_url": file_url,
            })
            .select(RESUME_COLUMNS)
            .single()
            .execute()
        )
    except Exception:
        try:
            supabase.storage.from_(settings.STORAGE_BUCKET).remove([storage_path])
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create resume record",
        ) from None
    return result.data
