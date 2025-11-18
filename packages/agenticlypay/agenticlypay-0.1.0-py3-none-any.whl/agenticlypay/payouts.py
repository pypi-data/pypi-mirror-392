"""Monthly payout management system."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from agenticlypay.stripe_client import StripeClient
from agenticlypay.config import config


class PayoutManager:
    """Manages monthly payouts to developers."""

    def __init__(self):
        """Initialize the payout manager."""
        self.stripe_client = StripeClient()

    def calculate_monthly_earnings(
        self, developer_account_id: str, year: int, month: int
    ) -> Dict[str, Any]:
        """
        Calculate monthly earnings for a developer.

        Args:
            developer_account_id: Connected account ID
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Dictionary with earnings breakdown
        """
        # Calculate date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # List charges for the connected account in the date range
        charges = self.stripe_client.list_charges(
            limit=100,
            created={"gte": start_timestamp, "lt": end_timestamp},
        )

        total_amount = 0
        total_fees = 0
        transaction_count = 0

        # Filter charges for this developer account
        for charge in charges.data:
            # Check if charge is associated with this developer account
            if hasattr(charge, "destination") and charge.destination == developer_account_id:
                total_amount += charge.amount
                # Calculate fee that was deducted
                fee = config.calculate_fee(charge.amount)
                total_fees += fee
                transaction_count += 1

        net_amount = total_amount - total_fees

        return {
            "developer_account_id": developer_account_id,
            "year": year,
            "month": month,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_amount": total_amount,
            "total_fees": total_fees,
            "net_amount": net_amount,
            "transaction_count": transaction_count,
            "currency": "usd",
        }

    def create_monthly_payout(
        self, developer_account_id: str, year: int, month: int
    ) -> Dict[str, Any]:
        """
        Create a monthly payout for a developer.

        Args:
            developer_account_id: Connected account ID
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Dictionary with payout information
        """
        # Calculate earnings
        earnings = self.calculate_monthly_earnings(developer_account_id, year, month)

        if earnings["net_amount"] <= 0:
            return {
                "success": False,
                "message": "No earnings to payout",
                "earnings": earnings,
            }

        # Create transfer to connected account
        transfer = self.stripe_client.create_transfer(
            amount=earnings["net_amount"],
            currency="usd",
            destination=developer_account_id,
            metadata={
                "payout_type": "monthly",
                "year": str(year),
                "month": str(month),
                "transaction_count": str(earnings["transaction_count"]),
            },
        )

        return {
            "success": True,
            "transfer_id": transfer.id,
            "amount": transfer.amount,
            "currency": transfer.currency,
            "destination": transfer.destination,
            "earnings": earnings,
            "created": transfer.created,
        }

    def process_all_monthly_payouts(
        self, year: int, month: int, developer_account_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process monthly payouts for all developers or specified accounts.

        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            developer_account_ids: List of account IDs (None for all)

        Returns:
            Dictionary with payout results
        """
        results = {
            "year": year,
            "month": month,
            "processed": [],
            "failed": [],
            "skipped": [],
        }

        # If no account IDs provided, you would need to retrieve all connected accounts
        # For now, this is a placeholder that requires account IDs
        if not developer_account_ids:
            # TODO: Implement retrieval of all connected accounts
            return {
                "error": "developer_account_ids must be provided",
                "results": results,
            }

        for account_id in developer_account_ids:
            try:
                payout = self.create_monthly_payout(account_id, year, month)
                if payout["success"]:
                    results["processed"].append(payout)
                else:
                    results["skipped"].append(
                        {
                            "account_id": account_id,
                            "reason": payout["message"],
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

    def get_payout_history(
        self, developer_account_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get payout history for a developer.

        Args:
            developer_account_id: Connected account ID
            limit: Maximum number of payouts to return

        Returns:
            List of payout dictionaries
        """
        # List transfers to this account
        import stripe
        transfers = stripe.Transfer.list(
            destination=developer_account_id, limit=limit
        )

        payouts = []
        for transfer in transfers.data:
            if transfer.metadata.get("payout_type") == "monthly":
                payouts.append(
                    {
                        "transfer_id": transfer.id,
                        "amount": transfer.amount,
                        "currency": transfer.currency,
                        "year": transfer.metadata.get("year"),
                        "month": transfer.metadata.get("month"),
                        "transaction_count": transfer.metadata.get("transaction_count"),
                        "created": transfer.created,
                        "status": transfer.status,
                    }
                )

        return payouts

