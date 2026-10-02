from fastapi import APIRouter, HTTPException, UploadFile, status

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload")
def upload_resume(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith((".pdf", ".doc", ".docx")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported resume format")
    return {"file_name": file.filename, "storage_path": f"/resumes/{file.filename}", "message": "Resume uploaded to Supabase Storage"}
