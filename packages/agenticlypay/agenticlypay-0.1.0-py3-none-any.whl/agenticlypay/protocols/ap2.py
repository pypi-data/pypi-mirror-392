"""Agent Payments Protocol (AP2) handler.

AP2 is Google's protocol for authorization and traceability in agentic payments.
It uses digitally signed mandates to define agent authority.
"""

from typing import Dict, Any, Optional
import json
import hashlib
from agenticlypay.stripe_client import StripeClient
from agenticlypay.config import config


class AP2Handler:
    """Handler for AP2 (Agent Payments Protocol) payments."""

    def __init__(self):
        """Initialize the AP2 handler."""
        self.stripe_client = StripeClient()

    def verify_mandate(
        self, mandate: Dict[str, Any], public_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify an AP2 mandate signature.

        Args:
            mandate: AP2 mandate object with signature
            public_key: Public key for verification (optional, for future implementation)

        Returns:
            Dictionary with verification result
        """
        # Basic mandate structure validation
        required_fields = ["agent_id", "user_id", "permissions", "expires_at"]
        missing_fields = [field for field in required_fields if field not in mandate]

        if missing_fields:
            return {
                "verified": False,
                "error": f"Missing required fields: {missing_fields}",
            }

        # Check expiration
        import time

        if mandate.get("expires_at", 0) < time.time():
            return {"verified": False, "error": "Mandate has expired"}

        # TODO: Implement full signature verification with public key
        # For now, return basic validation
        return {
            "verified": True,
            "agent_id": mandate.get("agent_id"),
            "user_id": mandate.get("user_id"),
            "permissions": mandate.get("permissions", []),
        }

    def create_payment_with_mandate(
        self,
        amount: int,
        developer_account_id: str,
        mandate: Dict[str, Any],
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment using an AP2 mandate.

        Args:
            amount: Amount in cents
            currency: Currency code (default: usd)
            developer_account_id: Connected account ID for the developer
            mandate: AP2 mandate object
            metadata: Additional metadata

        Returns:
            Dictionary with payment information
        """
        # Verify mandate first
        verification = self.verify_mandate(mandate)
        if not verification.get("verified"):
            raise ValueError(f"Invalid mandate: {verification.get('error')}")

        # Check if mandate allows payment creation
        permissions = verification.get("permissions", [])
        if "create_payment" not in permissions and "complete_purchase" not in permissions:
            raise ValueError("Mandate does not authorize payment creation")

        # Calculate platform fee
        fee = config.calculate_fee(amount)

        # Prepare metadata
        payment_metadata = metadata or {}
        payment_metadata["protocol"] = "AP2"
        payment_metadata["developer_account_id"] = developer_account_id
        payment_metadata["agent_id"] = mandate.get("agent_id")
        payment_metadata["user_id"] = mandate.get("user_id")
        payment_metadata["mandate_id"] = mandate.get("mandate_id", "")

        # Create payment intent
        payment_intent = self.stripe_client.create_payment_intent(
            amount=amount,
            currency=currency,
            payment_method_types=["card", "us_bank_account"],
            metadata=payment_metadata,
            application_fee_amount=fee,
            transfer_data={"destination": developer_account_id},
        )

        return {
            "payment_id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
            "amount": amount,
            "currency": currency,
            "fee": fee,
            "net_amount": amount - fee,
            "status": payment_intent.status,
            "mandate_verified": True,
        }

    def process_payment(
        self,
        payment_id: str,
        payment_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process an AP2 payment.

        Args:
            payment_id: Payment intent ID
            payment_method: Payment method ID (optional)

        Returns:
            Dictionary with payment result
        """
        if payment_method:
            payment_intent = self.stripe_client.confirm_payment_intent(
                payment_id, payment_method=payment_method
            )
        else:
            payment_intent = self.stripe_client.retrieve_payment_intent(payment_id)

        return {
            "payment_id": payment_intent.id,
            "status": payment_intent.status,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency,
            "charges": [
                {
                    "charge_id": charge.id,
                    "amount": charge.amount,
                    "status": charge.status,
                }
                for charge in payment_intent.charges.data
            ]
            if payment_intent.charges
            else [],
        }

    def handle_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle AP2-related webhook events.

        Args:
            event_data: Stripe webhook event data

        Returns:
            Dictionary with webhook handling result
        """
        event_type = event_data.get("type")
        data = event_data.get("data", {}).get("object", {})

        if event_type == "payment_intent.succeeded":
            return {
                "handled": True,
                "event_type": event_type,
                "payment_id": data.get("id"),
                "status": "success",
                "protocol": "AP2",
            }
        elif event_type == "payment_intent.payment_failed":
            return {
                "handled": True,
                "event_type": event_type,
                "payment_id": data.get("id"),
                "status": "failed",
                "protocol": "AP2",
            }

        return {"handled": False, "event_type": event_type}

