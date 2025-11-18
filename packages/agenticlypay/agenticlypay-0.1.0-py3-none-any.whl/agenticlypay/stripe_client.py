"""Stripe API client wrapper."""

import stripe
from typing import Optional, Dict, Any
from agenticlypay.config import config

# Initialize Stripe with API key (if available)
if config.stripe_secret_key:
    stripe.api_key = config.stripe_secret_key


class StripeClient:
    """Wrapper for Stripe API operations."""

    @staticmethod
    def create_payment_intent(
        amount: int,
        currency: str = "usd",
        payment_method_types: Optional[list] = None,
        metadata: Optional[Dict[str, str]] = None,
        application_fee_amount: Optional[int] = None,
        transfer_data: Optional[Dict[str, str]] = None,
    ) -> stripe.PaymentIntent:
        """
        Create a payment intent.

        Args:
            amount: Amount in cents
            currency: Currency code (default: usd)
            payment_method_types: List of payment method types
            metadata: Additional metadata
            application_fee_amount: Application fee in cents
            transfer_data: Transfer data for Connect accounts

        Returns:
            PaymentIntent object
        """
        params: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "payment_method_types": payment_method_types or ["card"],
        }

        if metadata:
            params["metadata"] = metadata

        if application_fee_amount:
            params["application_fee_amount"] = application_fee_amount

        if transfer_data:
            params["transfer_data"] = transfer_data

        return stripe.PaymentIntent.create(**params)

    @staticmethod
    def confirm_payment_intent(
        payment_intent_id: str, payment_method: Optional[str] = None
    ) -> stripe.PaymentIntent:
        """
        Confirm a payment intent.

        Args:
            payment_intent_id: Payment intent ID
            payment_method: Payment method ID

        Returns:
            Confirmed PaymentIntent object
        """
        params: Dict[str, Any] = {}
        if payment_method:
            params["payment_method"] = payment_method

        return stripe.PaymentIntent.confirm(payment_intent_id, **params)

    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> stripe.PaymentIntent:
        """
        Retrieve a payment intent.

        Args:
            payment_intent_id: Payment intent ID

        Returns:
            PaymentIntent object
        """
        return stripe.PaymentIntent.retrieve(payment_intent_id)

    @staticmethod
    def create_account(
        type: str = "express",
        country: str = "US",
        email: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> stripe.Account:
        """
        Create a Stripe Connect account.

        Args:
            type: Account type (express, standard, custom)
            country: Country code
            email: Account email
            metadata: Additional metadata

        Returns:
            Account object
        """
        params: Dict[str, Any] = {
            "type": type,
            "country": country,
        }

        if email:
            params["email"] = email

        if metadata:
            params["metadata"] = metadata

        return stripe.Account.create(**params)

    @staticmethod
    def create_account_link(
        account_id: str,
        refresh_url: str,
        return_url: str,
        type: str = "account_onboarding",
    ) -> stripe.AccountLink:
        """
        Create an account link for onboarding.

        Args:
            account_id: Connected account ID
            refresh_url: URL to redirect if link expires
            return_url: URL to redirect after completion
            type: Link type (account_onboarding, account_update)

        Returns:
            AccountLink object
        """
        return stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type=type,
        )

    @staticmethod
    def retrieve_account(account_id: str) -> stripe.Account:
        """
        Retrieve a connected account.

        Args:
            account_id: Account ID

        Returns:
            Account object
        """
        return stripe.Account.retrieve(account_id)

    @staticmethod
    def create_transfer(
        amount: int,
        currency: str,
        destination: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> stripe.Transfer:
        """
        Create a transfer to a connected account.

        Args:
            amount: Amount in cents
            currency: Currency code
            destination: Connected account ID
            metadata: Additional metadata

        Returns:
            Transfer object
        """
        params: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "destination": destination,
        }

        if metadata:
            params["metadata"] = metadata

        return stripe.Transfer.create(**params)

    @staticmethod
    def list_charges(
        limit: int = 100,
        created: Optional[Dict[str, int]] = None,
        transfer_group: Optional[str] = None,
    ) -> stripe.ListObject:
        """
        List charges.

        Args:
            limit: Maximum number of charges to return
            created: Filter by creation date
            transfer_group: Filter by transfer group

        Returns:
            List of Charge objects
        """
        params: Dict[str, Any] = {"limit": limit}

        if created:
            params["created"] = created

        if transfer_group:
            params["transfer_group"] = transfer_group

        return stripe.Charge.list(**params)

    @staticmethod
    def create_tax_form(
        account_id: str, form_type: str = "us_1099_misc"
    ) -> Dict[str, Any]:
        """
        Create a tax form for a connected account.

        Args:
            account_id: Connected account ID
            form_type: Type of tax form (default: us_1099_misc)

        Returns:
            Tax form dictionary
        """
        # Note: Stripe Tax API may require different approach
        # For now, return a placeholder structure
        # In production, use Stripe's Tax Reporting API or 1099 API
        return {
            "account": account_id,
            "type": form_type,
            "status": "pending",
            "note": "Tax form generation - use Stripe Dashboard or Tax API for actual generation"
        }

    @staticmethod
    def construct_webhook_event(
        payload: bytes, sig_header: str, secret: Optional[str] = None
    ) -> stripe.Event:
        """
        Construct and verify a webhook event.

        Args:
            payload: Webhook payload
            sig_header: Stripe signature header
            secret: Webhook secret (uses config if not provided)

        Returns:
            Event object
        """
        webhook_secret = secret or config.stripe_webhook_secret
        if not webhook_secret:
            raise ValueError("Webhook secret not configured")

        return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

