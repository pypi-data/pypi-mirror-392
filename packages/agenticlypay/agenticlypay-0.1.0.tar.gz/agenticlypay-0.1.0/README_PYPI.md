# AgenticlyPay

A Python library for processing agentic payments (ACP, AP2, x402) via Stripe. Built for agentic developers who need automated payment processing, monthly payouts, and tax compliance.

## Features

- **Multi-Protocol Support**: Process payments using ACP (Agentic Commerce Protocol), AP2 (Agent Payments Protocol), or x402 protocols
- **Stripe Connect Integration**: Seamless onboarding and account management for developers
- **Automated Payouts**: Monthly automated payouts to developer Stripe accounts
- **Tax Compliance**: Automatic 1099 form generation and filing
- **Transparent Pricing**: 6.5% + $0.30 per transaction
- **RESTful API**: Complete API for integration into any application

## Installation

```bash
pip install agenticlypay
```

## Quick Start

### Basic Usage

```python
from agenticlypay import PaymentProcessor, ConnectManager

# Initialize components
payment_processor = PaymentProcessor()
connect_manager = ConnectManager()

# Create a developer account
account = connect_manager.create_developer_account(
    email="developer@example.com",
    country="US"
)

# Process an ACP payment
result = payment_processor.process_payment(
    protocol="ACP",
    amount=10000,  # $100.00 in cents
    developer_account_id=account["account_id"],
    currency="usd"
)
```

### ACP Payment Example

```python
from agenticlypay import PaymentProcessor

processor = PaymentProcessor()

result = processor.process_payment(
    protocol="ACP",
    amount=10000,  # $100.00 in cents
    currency="usd",
    developer_account_id="acct_xxxxx",
    description="Payment for service"
)
```

### AP2 Payment Example

```python
result = processor.process_payment(
    protocol="AP2",
    amount=10000,
    currency="usd",
    developer_account_id="acct_xxxxx",
    mandate={
        "agent_id": "agent_123",
        "user_id": "user_456",
        "permissions": ["create_payment", "complete_purchase"],
        "expires_at": 1735689600,
        "mandate_id": "mandate_789"
    }
)
```

### x402 Payment Example

```python
result = processor.process_payment(
    protocol="x402",
    amount=10000,
    currency="usd",
    developer_account_id="acct_xxxxx",
    resource_url="/api/data/endpoint"
)
```

## Configuration

Set environment variables or use a `.env` file:

```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
PLATFORM_FEE_PERCENTAGE=0.065
PLATFORM_FEE_FIXED=30
```

## API Documentation

For complete API documentation and integration guides, visit:
https://agenticlypay-frontend-r6zgzqpgja-uc.a.run.app

## License

MIT License

## Support

For issues and questions, please visit our GitHub repository or contact support@agenticlypay.com

