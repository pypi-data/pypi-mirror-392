"""
AgenticlyPay - Python library for processing agentic payments via Stripe.

Supports ACP (Agentic Commerce Protocol), AP2 (Agent Payments Protocol), and x402 protocols.
"""

__version__ = "0.1.0"
__author__ = "AgenticlyPay"
__email__ = "support@agenticlypay.com"

from agenticlypay.config import Config
from agenticlypay.stripe_client import StripeClient
from agenticlypay.connect import ConnectManager
from agenticlypay.payments import PaymentProcessor

__all__ = [
    "Config",
    "StripeClient",
    "ConnectManager",
    "PaymentProcessor",
]

