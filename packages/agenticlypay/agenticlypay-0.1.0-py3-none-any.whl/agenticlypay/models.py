"""Data models for tracking transactions and accounts."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DeveloperAccount(BaseModel):
    """Model for developer account information."""

    account_id: str
    email: str
    country: str = "US"
    charges_enabled: bool = False
    payouts_enabled: bool = False
    details_submitted: bool = False
    created: int
    metadata: Dict[str, str] = Field(default_factory=dict)


class Transaction(BaseModel):
    """Model for payment transaction."""

    transaction_id: str
    payment_intent_id: str
    developer_account_id: str
    protocol: str  # ACP, AP2, or x402
    amount: int  # in cents
    currency: str = "usd"
    fee: int  # in cents
    net_amount: int  # in cents
    status: str
    created: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Payout(BaseModel):
    """Model for monthly payout."""

    payout_id: str
    transfer_id: str
    developer_account_id: str
    year: int
    month: int
    amount: int  # in cents
    currency: str = "usd"
    transaction_count: int
    created: int
    status: str


class TaxForm(BaseModel):
    """Model for 1099 tax form."""

    form_id: Optional[str] = None
    developer_account_id: str
    year: int
    amount: int  # in cents
    form_type: str = "us_1099_misc"
    status: str = "pending"
    created: Optional[int] = None

