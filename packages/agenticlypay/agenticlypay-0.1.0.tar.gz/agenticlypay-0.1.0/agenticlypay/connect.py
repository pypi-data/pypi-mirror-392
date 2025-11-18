"""Stripe Connect integration for developer account management."""

from typing import Optional, Dict, Any
from agenticlypay.stripe_client import StripeClient
from agenticlypay.config import config


class ConnectManager:
    """Manages Stripe Connect accounts for developers."""

    def __init__(self):
        """Initialize the Connect manager."""
        self.stripe_client = StripeClient()

    def create_developer_account(
        self,
        email: str,
        country: str = "US",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new Express account for a developer.

        Args:
            email: Developer email address
            country: Country code (default: US)
            metadata: Additional metadata to store

        Returns:
            Dictionary with account information
        """
        account_metadata = metadata or {}
        account_metadata["platform"] = config.platform_name

        account = self.stripe_client.create_account(
            type="express",
            country=country,
            email=email,
            metadata=account_metadata,
        )

        return {
            "account_id": account.id,
            "email": account.email,
            "country": account.country,
            "type": account.type,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "created": account.created,
        }

    def create_onboarding_link(
        self,
        account_id: str,
        refresh_url: str,
        return_url: str,
    ) -> Dict[str, Any]:
        """
        Create an onboarding link for a developer account.

        Args:
            account_id: Stripe Connect account ID
            refresh_url: URL to redirect if link expires
            return_url: URL to redirect after onboarding completion

        Returns:
            Dictionary with onboarding link URL
        """
        account_link = self.stripe_client.create_account_link(
            account_id=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

        return {
            "url": account_link.url,
            "expires_at": account_link.expires_at,
        }

    def get_account_status(self, account_id: str) -> Dict[str, Any]:
        """
        Get the status of a developer account.

        Args:
            account_id: Stripe Connect account ID

        Returns:
            Dictionary with account status information
        """
        account = self.stripe_client.retrieve_account(account_id)

        return {
            "account_id": account.id,
            "email": account.email,
            "country": account.country,
            "type": account.type,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "details_submitted": account.details_submitted,
            "payments_enabled": getattr(account, "payments_enabled", False),
            "created": account.created,
        }

    def update_account_metadata(
        self, account_id: str, metadata: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Update metadata for a developer account.

        Args:
            account_id: Stripe Connect account ID
            metadata: Metadata to update

        Returns:
            Updated account information
        """
        account = self.stripe_client.retrieve_account(account_id)
        account.metadata.update(metadata)
        account.save()

        return {
            "account_id": account.id,
            "metadata": account.metadata,
        }

    def collect_tax_information(
        self, account_id: str, tax_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect and store tax information for a developer.

        Args:
            account_id: Stripe Connect account ID
            tax_info: Tax information dictionary

        Returns:
            Confirmation of tax information storage
        """
        # Store tax information in account metadata
        metadata = {
            "tax_collected": "true",
            "tax_name": tax_info.get("name", ""),
            "tax_ssn": tax_info.get("ssn", ""),
            "tax_ein": tax_info.get("ein", ""),
            "tax_address": tax_info.get("address", ""),
        }

        return self.update_account_metadata(account_id, metadata)

