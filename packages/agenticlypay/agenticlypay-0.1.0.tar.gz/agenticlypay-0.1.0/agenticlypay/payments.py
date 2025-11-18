"""Unified payment processing interface."""

from typing import Dict, Any, Optional, Literal
from agenticlypay.protocols.acp import ACPHandler
from agenticlypay.protocols.ap2 import AP2Handler
from agenticlypay.protocols.x402 import X402Handler
from agenticlypay.config import config


class PaymentProcessor:
    """Unified payment processor supporting ACP, AP2, and x402 protocols."""

    def __init__(self):
        """Initialize the payment processor with protocol handlers."""
        self.acp_handler = ACPHandler()
        self.ap2_handler = AP2Handler()
        self.x402_handler = X402Handler()

    def process_payment(
        self,
        protocol: Literal["ACP", "AP2", "x402"],
        amount: int,
        developer_account_id: str,
        currency: str = "usd",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Process a payment using the specified protocol.

        Args:
            protocol: Payment protocol (ACP, AP2, or x402)
            amount: Amount in cents
            currency: Currency code (default: usd)
            developer_account_id: Connected account ID for the developer
            **kwargs: Protocol-specific arguments

        Returns:
            Dictionary with payment information

        Raises:
            ValueError: If protocol is not supported
        """
        protocol = protocol.upper()

        if protocol == "ACP":
            return self.acp_handler.create_checkout(
                amount=amount,
                developer_account_id=developer_account_id,
                currency=currency,
                metadata=kwargs.get("metadata"),
                description=kwargs.get("description"),
            )

        elif protocol == "AP2":
            mandate = kwargs.get("mandate")
            if not mandate:
                raise ValueError("AP2 protocol requires a mandate")

            return self.ap2_handler.create_payment_with_mandate(
                amount=amount,
                developer_account_id=developer_account_id,
                mandate=mandate,
                currency=currency,
                metadata=kwargs.get("metadata"),
            )

        elif protocol == "X402" or protocol == "x402":
            return self.x402_handler.create_payment_request(
                amount=amount,
                developer_account_id=developer_account_id,
                currency=currency,
                resource_url=kwargs.get("resource_url"),
                metadata=kwargs.get("metadata"),
            )

        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def confirm_payment(
        self,
        protocol: Literal["ACP", "AP2", "x402"],
        payment_id: str,
        payment_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Confirm a payment using the specified protocol.

        Args:
            protocol: Payment protocol (ACP, AP2, or x402)
            payment_id: Payment intent ID
            payment_method: Payment method ID (optional)

        Returns:
            Dictionary with payment confirmation result

        Raises:
            ValueError: If protocol is not supported
        """
        protocol = protocol.upper()

        if protocol == "ACP":
            return self.acp_handler.process_payment(payment_id, payment_method)

        elif protocol == "AP2":
            return self.ap2_handler.process_payment(payment_id, payment_method)

        elif protocol == "X402" or protocol == "x402":
            return self.x402_handler.process_payment(payment_id, payment_method)

        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def get_payment_status(
        self,
        protocol: Literal["ACP", "AP2", "x402"],
        payment_id: str,
    ) -> Dict[str, Any]:
        """
        Get the status of a payment.

        Args:
            protocol: Payment protocol (ACP, AP2, or x402)
            payment_id: Payment intent ID

        Returns:
            Dictionary with payment status

        Raises:
            ValueError: If protocol is not supported
        """
        protocol = protocol.upper()

        if protocol == "ACP":
            return self.acp_handler.get_checkout_status(payment_id)

        elif protocol == "AP2" or protocol == "X402" or protocol == "x402":
            # Both AP2 and x402 can use the same status check
            from agenticlypay.stripe_client import StripeClient

            stripe_client = StripeClient()
            payment_intent = stripe_client.retrieve_payment_intent(payment_id)

            return {
                "payment_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "created": payment_intent.created,
                "metadata": payment_intent.metadata,
            }

        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def calculate_fee(self, amount_cents: int) -> Dict[str, Any]:
        """
        Calculate platform fee for a transaction.

        Args:
            amount_cents: Transaction amount in cents

        Returns:
            Dictionary with fee breakdown
        """
        fee = config.calculate_fee(amount_cents)
        net_amount = config.calculate_net_amount(amount_cents)

        return {
            "amount": amount_cents,
            "fee_percentage": config.platform_fee_percentage,
            "fee_fixed": config.platform_fee_fixed,
            "fee_total": fee,
            "net_amount": net_amount,
        }

    def handle_webhook(
        self, event_data: Dict[str, Any], protocol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle webhook events from Stripe.

        Args:
            event_data: Stripe webhook event data
            protocol: Protocol type if known (optional)

        Returns:
            Dictionary with webhook handling result
        """
        # Try to determine protocol from metadata
        if not protocol:
            metadata = event_data.get("data", {}).get("object", {}).get("metadata", {})
            protocol = metadata.get("protocol", "").upper()

        # Route to appropriate handler
        if protocol == "ACP":
            return self.acp_handler.handle_webhook(event_data)
        elif protocol == "AP2":
            return self.ap2_handler.handle_webhook(event_data)
        elif protocol == "X402" or protocol == "x402":
            return self.x402_handler.handle_webhook(event_data)
        else:
            # Generic webhook handling
            return {"handled": False, "event_type": event_data.get("type")}

