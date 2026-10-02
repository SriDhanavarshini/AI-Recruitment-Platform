from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_hr_user
from app.core.supabase import supabase
from app.schemas.schemas import CompanyCreate, CompanyOut

router = APIRouter(prefix="/companies", tags=["companies"])

COMPANY_COLUMNS = "id, name, created_by, created_at"


@router.get("", response_model=list[CompanyOut])
def list_companies(current_user: dict[str, Any] = Depends(require_hr_user)):
    try:
        result = (
            supabase.table("companies")
            .select(COMPANY_COLUMNS)
            .eq("created_by", current_user["auth_id"])
            .order("created_at", desc=True)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not retrieve companies",
        ) from None

    return result.data or []


@router.post("", response_model=CompanyOut)
def create_company(
    payload: CompanyCreate,
    current_user: dict[str, Any] = Depends(require_hr_user),
):
    try:
        result = (
            supabase.table("companies")
            .insert({"name": payload.name, "created_by": current_user["auth_id"]})
            .select(COMPANY_COLUMNS)
            .single()
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create company",
        ) from None

    return result.data


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: UUID,
    current_user: dict[str, Any] = Depends(require_hr_user),
):
    try:
        result = (
            supabase.table("companies")
            .select(COMPANY_COLUMNS)
            .eq("id", str(company_id))
            .eq("created_by", current_user["auth_id"])
            .maybe_single()
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not retrieve company",
        ) from None

    if result.data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return result.data
