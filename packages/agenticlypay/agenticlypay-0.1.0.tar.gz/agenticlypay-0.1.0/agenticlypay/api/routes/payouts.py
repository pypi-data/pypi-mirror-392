"""Payout management routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from agenticlypay.payouts import PayoutManager

router = APIRouter()
payout_manager = PayoutManager()


class CreatePayoutRequest(BaseModel):
    """Request model for creating a payout."""

    developer_account_id: str
    year: int
    month: int


class ProcessPayoutsRequest(BaseModel):
    """Request model for processing payouts for multiple accounts."""

    year: int
    month: int
    developer_account_ids: Optional[List[str]] = None


@router.get("/earnings/{account_id}/{year}/{month}")
async def get_monthly_earnings(account_id: str, year: int, month: int):
    """Get monthly earnings for a developer."""
    try:
        earnings = payout_manager.calculate_monthly_earnings(account_id, year, month)
        return {"success": True, "earnings": earnings}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create")
async def create_payout(request: CreatePayoutRequest):
    """Create a monthly payout for a developer."""
    try:
        payout = payout_manager.create_monthly_payout(
            developer_account_id=request.developer_account_id,
            year=request.year,
            month=request.month,
        )
        return {"success": payout["success"], "payout": payout}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/process-all")
async def process_all_payouts(request: ProcessPayoutsRequest):
    """Process monthly payouts for all or specified developers."""
    try:
        results = payout_manager.process_all_monthly_payouts(
            year=request.year,
            month=request.month,
            developer_account_ids=request.developer_account_ids,
        )
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{account_id}")
async def get_payout_history(account_id: str, limit: int = 10):
    """Get payout history for a developer."""
    try:
        history = payout_manager.get_payout_history(account_id, limit=limit)
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

