"""Webhook handlers for Stripe events."""

from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import json
from agenticlypay.stripe_client import StripeClient
from agenticlypay.payments import PaymentProcessor

router = APIRouter()
stripe_client = StripeClient()
payment_processor = PaymentProcessor()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
):
    """Handle Stripe webhook events."""
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        payload = await request.body()
        event = stripe_client.construct_webhook_event(
            payload=payload, sig_header=stripe_signature
        )

        # Handle the event
        event_data = event.to_dict()
        result = payment_processor.handle_webhook(event_data)

        return {"success": True, "handled": result.get("handled", False), "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_webhook():
    """Test webhook endpoint."""
    return {"status": "webhook endpoint is active"}

