from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.schemas.schemas import TokenResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserCreate):
    if not payload.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")
    access_token = create_access_token(payload.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate):
    if not payload.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")
    access_token = create_access_token(payload.email)
    return {"access_token": access_token, "token_type": "bearer"}
