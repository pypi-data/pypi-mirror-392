"""Tax reporting routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from agenticlypay.tax import TaxReporter

router = APIRouter()
tax_reporter = TaxReporter()


class Generate1099Request(BaseModel):
    """Request model for generating a 1099 form."""

    developer_account_id: str
    year: int


class GenerateAll1099Request(BaseModel):
    """Request model for generating 1099 forms for all developers."""

    year: int
    developer_account_ids: Optional[List[str]] = None


@router.get("/earnings/{account_id}/{year}")
async def get_annual_earnings(account_id: str, year: int):
    """Get annual earnings for a developer."""
    try:
        earnings = tax_reporter.calculate_annual_earnings(account_id, year)
        return {"success": True, "earnings": earnings}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/1099/generate")
async def generate_1099(request: Generate1099Request):
    """Generate a 1099 form for a developer."""
    try:
        result = tax_reporter.generate_1099_form(
            developer_account_id=request.developer_account_id, year=request.year
        )
        return {"success": result["success"], "form": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/1099/generate-all")
async def generate_all_1099(request: GenerateAll1099Request):
    """Generate 1099 forms for all eligible developers."""
    try:
        results = tax_reporter.generate_all_1099_forms(
            year=request.year, developer_account_ids=request.developer_account_ids
        )
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/forms/{account_id}")
async def get_tax_forms(account_id: str, year: Optional[int] = None):
    """Get tax forms for a developer."""
    try:
        forms = tax_reporter.get_tax_forms(account_id, year=year)
        return {"success": True, "forms": forms}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

