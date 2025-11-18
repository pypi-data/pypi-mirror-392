"""Tax reporting and 1099 form generation."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from agenticlypay.stripe_client import StripeClient
from agenticlypay.payouts import PayoutManager


class TaxReporter:
    """Handles tax reporting and 1099 form generation."""

    def __init__(self):
        """Initialize the tax reporter."""
        self.stripe_client = StripeClient()
        self.payout_manager = PayoutManager()

    def calculate_annual_earnings(
        self, developer_account_id: str, year: int
    ) -> Dict[str, Any]:
        """
        Calculate total annual earnings for a developer.

        Args:
            developer_account_id: Connected account ID
            year: Year (e.g., 2024)

        Returns:
            Dictionary with annual earnings breakdown
        """
        total_amount = 0
        total_fees = 0
        total_transactions = 0
        monthly_breakdown = []

        # Calculate earnings for each month
        for month in range(1, 13):
            monthly_earnings = self.payout_manager.calculate_monthly_earnings(
                developer_account_id, year, month
            )
            total_amount += monthly_earnings["total_amount"]
            total_fees += monthly_earnings["total_fees"]
            total_transactions += monthly_earnings["transaction_count"]
            monthly_breakdown.append(monthly_earnings)

        net_amount = total_amount - total_fees

        return {
            "developer_account_id": developer_account_id,
            "year": year,
            "total_amount": total_amount,
            "total_fees": total_fees,
            "net_amount": net_amount,
            "total_transactions": total_transactions,
            "monthly_breakdown": monthly_breakdown,
            "currency": "usd",
        }

    def generate_1099_form(
        self, developer_account_id: str, year: int
    ) -> Dict[str, Any]:
        """
        Generate a 1099 form for a developer.

        Args:
            developer_account_id: Connected account ID
            year: Tax year (e.g., 2024)

        Returns:
            Dictionary with 1099 form information
        """
        # Calculate annual earnings
        annual_earnings = self.calculate_annual_earnings(developer_account_id, year)

        # IRS threshold for 1099-MISC is $600
        if annual_earnings["net_amount"] < 60000:  # $600 in cents
            return {
                "success": False,
                "message": "Earnings below $600 threshold, 1099 not required",
                "earnings": annual_earnings,
            }

        # Get account information for tax form
        account = self.stripe_client.retrieve_account(developer_account_id)

        # Create tax form via Stripe
        try:
            tax_form = self.stripe_client.create_tax_form(
                account_id=developer_account_id, form_type="us_1099_misc"
            )

            return {
                "success": True,
                "form_id": tax_form.id,
                "form_type": "us_1099_misc",
                "year": year,
                "developer_account_id": developer_account_id,
                "amount": annual_earnings["net_amount"],
                "earnings": annual_earnings,
                "status": getattr(tax_form, "status", "created"),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "earnings": annual_earnings,
            }

    def generate_all_1099_forms(
        self, year: int, developer_account_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate 1099 forms for all eligible developers.

        Args:
            year: Tax year (e.g., 2024)
            developer_account_ids: List of account IDs (None for all)

        Returns:
            Dictionary with generation results
        """
        results = {
            "year": year,
            "generated": [],
            "failed": [],
            "skipped": [],
        }

        # If no account IDs provided, you would need to retrieve all connected accounts
        if not developer_account_ids:
            # TODO: Implement retrieval of all connected accounts
            return {
                "error": "developer_account_ids must be provided",
                "results": results,
            }

        for account_id in developer_account_ids:
            try:
                form_result = self.generate_1099_form(account_id, year)
                if form_result["success"]:
                    results["generated"].append(form_result)
                else:
                    if "threshold" in form_result.get("message", "").lower():
                        results["skipped"].append(
                            {
                                "account_id": account_id,
                                "reason": form_result["message"],
                            }
                        )
                    else:
                        results["failed"].append(
                            {
                                "account_id": account_id,
                                "error": form_result.get("error", "Unknown error"),
                            }
                        )
            except Exception as e:
                results["failed"].append(
                    {
                        "account_id": account_id,
                        "error": str(e),
                    }
                )

        return results

    def get_tax_forms(
        self, developer_account_id: str, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get tax forms for a developer.

        Args:
            developer_account_id: Connected account ID
            year: Tax year (optional, defaults to current year)

        Returns:
            List of tax form dictionaries
        """
        if not year:
            year = datetime.now().year

        # Calculate annual earnings
        annual_earnings = self.calculate_annual_earnings(developer_account_id, year)

        # Try to retrieve tax form
        # Note: Stripe Tax API may have different methods for retrieving forms
        # This is a placeholder implementation
        return [
            {
                "year": year,
                "developer_account_id": developer_account_id,
                "amount": annual_earnings["net_amount"],
                "earnings": annual_earnings,
            }
        ]

