"""Stripe Connect account management routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from agenticlypay.connect import ConnectManager

router = APIRouter()
connect_manager = ConnectManager()


class CreateAccountRequest(BaseModel):
    """Request model for creating a developer account."""

    email: EmailStr
    country: str = "US"
    metadata: Optional[Dict[str, str]] = None


class CreateOnboardingLinkRequest(BaseModel):
    """Request model for creating an onboarding link."""

    account_id: str
    refresh_url: str
    return_url: str


class UpdateMetadataRequest(BaseModel):
    """Request model for updating account metadata."""

    account_id: str
    metadata: Dict[str, str]


class TaxInfoRequest(BaseModel):
    """Request model for tax information."""

    account_id: str
    name: str
    ssn: Optional[str] = None
    ein: Optional[str] = None
    address: str


@router.post("/accounts")
async def create_account(request: CreateAccountRequest):
    """Create a new Stripe Connect account for a developer."""
    try:
        account = connect_manager.create_developer_account(
            email=request.email,
            country=request.country,
            metadata=request.metadata,
        )
        return {"success": True, "account": account}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/{account_id}")
async def get_account(account_id: str):
    """Get account status."""
    try:
        status = connect_manager.get_account_status(account_id)
        return {"success": True, "account": status}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/onboarding")
async def create_onboarding_link(request: CreateOnboardingLinkRequest):
    """Create an onboarding link for a developer account."""
    try:
        link = connect_manager.create_onboarding_link(
            account_id=request.account_id,
            refresh_url=request.refresh_url,
            return_url=request.return_url,
        )
        return {"success": True, "onboarding_link": link}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/metadata")
async def update_metadata(request: UpdateMetadataRequest):
    """Update account metadata."""
    try:
        result = connect_manager.update_account_metadata(
            account_id=request.account_id, metadata=request.metadata
        )
        return {"success": True, "account": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tax-info")
async def collect_tax_info(request: TaxInfoRequest):
    """Collect tax information for a developer."""
    try:
        tax_info = {
            "name": request.name,
            "ssn": request.ssn,
            "ein": request.ein,
            "address": request.address,
        }
        result = connect_manager.collect_tax_information(
            account_id=request.account_id, tax_info=tax_info
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

