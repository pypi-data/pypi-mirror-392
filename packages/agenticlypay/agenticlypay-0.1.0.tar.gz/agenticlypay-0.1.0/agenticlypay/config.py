"""Configuration management for AgenticlyPay."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseSettings):
    """Application configuration."""

    # Stripe Configuration
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # Platform Configuration
    platform_fee_percentage: float = 0.065  # 6.5%
    platform_fee_fixed: int = 30  # $0.30 in cents
    platform_name: str = "AgenticlyPay"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False

    # Frontend Configuration
    frontend_url: str = "http://localhost:3000"

    # Cloud Run Configuration
    project_id: Optional[str] = None
    region: str = "us-central1"
    backend_service_name: str = "agenticlypay-backend"
    frontend_service_name: str = "agenticlypay-frontend"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def calculate_fee(self, amount_cents: int) -> int:
        """
        Calculate platform fee for a transaction.

        Args:
            amount_cents: Transaction amount in cents

        Returns:
            Fee amount in cents (6.5% + $0.30)
        """
        percentage_fee = int(amount_cents * self.platform_fee_percentage)
        return percentage_fee + self.platform_fee_fixed

    def calculate_net_amount(self, amount_cents: int) -> int:
        """
        Calculate net amount after platform fee.

        Args:
            amount_cents: Transaction amount in cents

        Returns:
            Net amount in cents (amount - fee)
        """
        fee = self.calculate_fee(amount_cents)
        return amount_cents - fee


# Global config instance
config = Config()

