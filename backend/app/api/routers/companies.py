from fastapi import APIRouter, HTTPException, status

from app.schemas.schemas import CompanyCreate, CompanyOut

router = APIRouter(prefix="/companies", tags=["companies"])

companies_db: dict[int, dict] = {}


@router.get("", response_model=list[CompanyOut])
def list_companies():
    return list(companies_db.values())


@router.post("", response_model=CompanyOut)
def create_company(payload: CompanyCreate):
    company_id = len(companies_db) + 1
    company = {"id": company_id, "owner_id": 1, **payload.model_dump()}
    companies_db[company_id] = company
    return company


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int):
    company = companies_db.get(company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company
