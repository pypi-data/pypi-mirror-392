# AgenticlyPay

A Python library and API service for processing agentic payments (ACP, AP2, x402) via Stripe. Built for agentic developers who need automated payment processing, monthly payouts, and tax compliance.

## Features

- **Multi-Protocol Support**: Process payments using ACP (Agentic Commerce Protocol), AP2 (Agent Payments Protocol), or x402 protocols
- **Stripe Connect Integration**: Seamless onboarding and account management for developers
- **Automated Payouts**: Monthly automated payouts to developer Stripe accounts
- **Tax Compliance**: Automatic 1099 form generation and filing
- **Transparent Pricing**: 6.5% + $0.30 per transaction
- **RESTful API**: Complete API for integration into any application
- **Web Dashboard**: Frontend website with detailed integration instructions

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your Stripe credentials:

```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
PLATFORM_FEE_PERCENTAGE=0.065
PLATFORM_FEE_FIXED=30
FRONTEND_URL=http://localhost:3000
```

### Running the Backend API

```bash
uvicorn agenticlypay.api.main:app --host 0.0.0.0 --port 8000
```

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

```bash
docker-compose up
```

## API Documentation

### Base URL

- Local: `http://localhost:8000`
- Production: `https://api.agenticlypay.com`

### Endpoints

#### Connect (Account Management)

- `POST /api/v1/connect/accounts` - Create a developer account
- `GET /api/v1/connect/accounts/{account_id}` - Get account status
- `POST /api/v1/connect/onboarding` - Create onboarding link
- `PUT /api/v1/connect/metadata` - Update account metadata
- `POST /api/v1/connect/tax-info` - Collect tax information

#### Payments

- `POST /api/v1/payments/process` - Process a payment (ACP/AP2/x402)
- `POST /api/v1/payments/confirm` - Confirm a payment
- `GET /api/v1/payments/status/{protocol}/{payment_id}` - Get payment status
- `GET /api/v1/payments/fee/{amount}` - Calculate platform fee

#### Payouts

- `GET /api/v1/payouts/earnings/{account_id}/{year}/{month}` - Get monthly earnings
- `POST /api/v1/payouts/create` - Create a monthly payout
- `POST /api/v1/payouts/process-all` - Process payouts for all developers
- `GET /api/v1/payouts/history/{account_id}` - Get payout history

#### Tax Reporting

- `GET /api/v1/tax/earnings/{account_id}/{year}` - Get annual earnings
- `POST /api/v1/tax/1099/generate` - Generate 1099 form
- `POST /api/v1/tax/1099/generate-all` - Generate 1099 forms for all developers
- `GET /api/v1/tax/forms/{account_id}` - Get tax forms

#### Webhooks

- `POST /api/v1/webhooks/stripe` - Stripe webhook handler

## Integration Examples

### ACP Payment

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

### AP2 Payment

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

### x402 Payment

```python
result = processor.process_payment(
    protocol="x402",
    amount=10000,
    currency="usd",
    developer_account_id="acct_xxxxx",
    resource_url="/api/data/endpoint"
)
```

## Deployment to Google Cloud Run

### Prerequisites

1. Google Cloud SDK installed
2. Docker installed
3. GCP project created

### Deploy

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Create secrets in GCP Secret Manager
gcloud secrets create stripe-secret-key --data-file=- <<< "sk_live_..."
gcloud secrets create stripe-webhook-secret --data-file=- <<< "whsec_..."

# Run deployment script
./scripts/deploy.sh
```

## Project Structure

```
agenticlypay-com/
├── agenticlypay/          # Python package
│   ├── api/              # FastAPI application
│   ├── protocols/        # Payment protocol handlers
│   ├── connect.py        # Stripe Connect integration
│   ├── payments.py       # Payment processing
│   ├── payouts.py        # Payout management
│   └── tax.py            # Tax reporting
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js app directory
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   └── Dockerfile
├── Dockerfile.backend    # Backend container
├── docker-compose.yml    # Local development
├── cloud-run-*.yaml      # Cloud Run configs
└── scripts/              # Deployment scripts
```

## Development

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn agenticlypay.api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Testing

```bash
# Backend tests (when implemented)
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## License

MIT

## Support

For integration help, visit the [frontend website](http://localhost:3000) which contains detailed, agent-readable integration instructions.

