"""Payment processing routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from agenticlypay.payments import PaymentProcessor

router = APIRouter()
payment_processor = PaymentProcessor()


class ProcessPaymentRequest(BaseModel):
    """Request model for processing a payment."""

    protocol: Literal["ACP", "AP2", "x402"]
    amount: int  # in cents
    currency: str = "usd"
    developer_account_id: str
    metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    mandate: Optional[Dict[str, Any]] = None  # Required for AP2
    resource_url: Optional[str] = None  # Optional for x402


class ConfirmPaymentRequest(BaseModel):
    """Request model for confirming a payment."""

    protocol: Literal["ACP", "AP2", "x402"]
    payment_id: str
    payment_method: Optional[str] = None


@router.post("/process")
async def process_payment(request: ProcessPaymentRequest):
    """Process a payment using the specified protocol."""
    try:
        result = payment_processor.process_payment(
            protocol=request.protocol,
            amount=request.amount,
            currency=request.currency,
            developer_account_id=request.developer_account_id,
            metadata=request.metadata,
            description=request.description,
            mandate=request.mandate,
            resource_url=request.resource_url,
        )
        return {"success": True, "payment": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm")
async def confirm_payment(request: ConfirmPaymentRequest):
    """Confirm a payment."""
    try:
        result = payment_processor.confirm_payment(
            protocol=request.protocol,
            payment_id=request.payment_id,
            payment_method=request.payment_method,
        )
        return {"success": True, "payment": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{protocol}/{payment_id}")
async def get_payment_status(protocol: str, payment_id: str):
    """Get payment status."""
    try:
        result = payment_processor.get_payment_status(
            protocol=protocol.upper(), payment_id=payment_id
        )
        return {"success": True, "status": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fee/{amount}")
async def calculate_fee(amount: int):
    """Calculate platform fee for an amount."""
    try:
        result = payment_processor.calculate_fee(amount)
        return {"success": True, "fee": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

