"""Agentic Commerce Protocol (ACP) handler.

ACP is an open standard developed by OpenAI and Stripe for agent-initiated commerce.
See: https://docs.stripe.com/agentic-commerce/protocol
"""

from typing import Dict, Any, Optional
from agenticlypay.stripe_client import StripeClient
from agenticlypay.config import config


class ACPHandler:
    """Handler for ACP (Agentic Commerce Protocol) payments."""

    def __init__(self):
        """Initialize the ACP handler."""
        self.stripe_client = StripeClient()

    def create_checkout(
        self,
        amount: int,
        developer_account_id: str,
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an ACP checkout session.

        Args:
            amount: Amount in cents
            currency: Currency code (default: usd)
            developer_account_id: Connected account ID for the developer
            metadata: Additional metadata
            description: Payment description

        Returns:
            Dictionary with checkout information
        """
        # Calculate platform fee
        fee = config.calculate_fee(amount)

        # Prepare metadata
        checkout_metadata = metadata or {}
        checkout_metadata["protocol"] = "ACP"
        checkout_metadata["developer_account_id"] = developer_account_id

        if description:
            checkout_metadata["description"] = description

        # Create payment intent with application fee
        payment_intent = self.stripe_client.create_payment_intent(
            amount=amount,
            currency=currency,
            payment_method_types=["card", "us_bank_account"],
            metadata=checkout_metadata,
            application_fee_amount=fee,
            transfer_data={"destination": developer_account_id},
        )

        return {
            "checkout_id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
            "amount": amount,
            "currency": currency,
            "fee": fee,
            "net_amount": amount - fee,
            "status": payment_intent.status,
        }

    def process_payment(
        self,
        checkout_id: str,
        payment_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process an ACP payment.

        Args:
            checkout_id: Payment intent ID (from create_checkout)
            payment_method: Payment method ID (optional)

        Returns:
            Dictionary with payment result
        """
        if payment_method:
            payment_intent = self.stripe_client.confirm_payment_intent(
                checkout_id, payment_method=payment_method
            )
        else:
            payment_intent = self.stripe_client.retrieve_payment_intent(checkout_id)

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

    def get_checkout_status(self, checkout_id: str) -> Dict[str, Any]:
        """
        Get the status of an ACP checkout.

        Args:
            checkout_id: Payment intent ID

        Returns:
            Dictionary with checkout status
        """
        payment_intent = self.stripe_client.retrieve_payment_intent(checkout_id)

        return {
            "checkout_id": payment_intent.id,
            "status": payment_intent.status,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency,
            "created": payment_intent.created,
            "metadata": payment_intent.metadata,
        }

    def handle_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle ACP-related webhook events.

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
            }
        elif event_type == "payment_intent.payment_failed":
            return {
                "handled": True,
                "event_type": event_type,
                "payment_id": data.get("id"),
                "status": "failed",
            }

        return {"handled": False, "event_type": event_type}

