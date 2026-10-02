from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": 1,
        "email": "candidate@example.com",
        "full_name": "Candidate User",
        "role": "CANDIDATE",
    }
