"""x402 protocol handler.

x402 is Coinbase's protocol that uses HTTP 402 status code for programmatic payments.
It enables instant, on-chain payments for microtransactions and API access.
"""

from typing import Dict, Any, Optional
from agenticlypay.stripe_client import StripeClient
from agenticlypay.config import config


class X402Handler:
    """Handler for x402 protocol payments."""

    def __init__(self):
        """Initialize the x402 handler."""
        self.stripe_client = StripeClient()

    def create_payment_request(
        self,
        amount: int,
        developer_account_id: str,
        currency: str = "usd",
        resource_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an x402 payment request (HTTP 402 response).

        Args:
            amount: Amount in cents
            currency: Currency code (default: usd)
            developer_account_id: Connected account ID for the developer
            resource_url: URL of the resource requiring payment
            metadata: Additional metadata

        Returns:
            Dictionary with x402 payment request information
        """
        # Calculate platform fee
        fee = config.calculate_fee(amount)

        # Prepare metadata
        payment_metadata = metadata or {}
        payment_metadata["protocol"] = "x402"
        payment_metadata["developer_account_id"] = developer_account_id

        if resource_url:
            payment_metadata["resource_url"] = resource_url

        # Create payment intent
        payment_intent = self.stripe_client.create_payment_intent(
            amount=amount,
            currency=currency,
            payment_method_types=["card", "us_bank_account"],
            metadata=payment_metadata,
            application_fee_amount=fee,
            transfer_data={"destination": developer_account_id},
        )

        # x402 response format
        return {
            "status": 402,
            "payment_required": True,
            "payment_intent": {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount,
                "currency": currency,
            },
            "fee": fee,
            "net_amount": amount - fee,
            "payment_url": f"/pay/{payment_intent.id}",
            "resource_url": resource_url,
        }

    def process_payment(
        self,
        payment_id: str,
        payment_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process an x402 payment.

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
            "status": 200 if payment_intent.status == "succeeded" else 402,
            "payment_id": payment_intent.id,
            "payment_status": payment_intent.status,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency,
            "paid": payment_intent.status == "succeeded",
        }

    def handle_http_402_request(
        self,
        resource_path: str,
        amount: int,
        developer_account_id: str,
        currency: str = "usd",
    ) -> Dict[str, Any]:
        """
        Handle an HTTP 402 request for a resource.

        Args:
            resource_path: Path to the resource requiring payment
            amount: Amount in cents
            currency: Currency code (default: usd)
            developer_account_id: Connected account ID for the developer

        Returns:
            x402 payment request response
        """
        return self.create_payment_request(
            amount=amount,
            currency=currency,
            developer_account_id=developer_account_id,
            resource_url=resource_path,
        )

    def verify_payment_for_resource(
        self, resource_path: str, payment_id: str
    ) -> Dict[str, Any]:
        """
        Verify that payment has been made for a resource.

        Args:
            resource_path: Path to the resource
            payment_id: Payment intent ID

        Returns:
            Dictionary with verification result
        """
        payment_intent = self.stripe_client.retrieve_payment_intent(payment_id)

        # Check if payment succeeded and matches resource
        resource_match = (
            payment_intent.metadata.get("resource_url") == resource_path
            or payment_intent.metadata.get("protocol") == "x402"
        )

        return {
            "verified": payment_intent.status == "succeeded" and resource_match,
            "payment_id": payment_id,
            "status": payment_intent.status,
            "amount": payment_intent.amount,
            "resource_path": resource_path,
        }

    def handle_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle x402-related webhook events.

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
                "protocol": "x402",
            }
        elif event_type == "payment_intent.payment_failed":
            return {
                "handled": True,
                "event_type": event_type,
                "payment_id": data.get("id"),
                "status": "failed",
                "protocol": "x402",
            }

        return {"handled": False, "event_type": event_type}

