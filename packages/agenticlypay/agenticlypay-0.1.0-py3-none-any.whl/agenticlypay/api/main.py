"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agenticlypay.config import config
from agenticlypay.api.routes import (
    connect,
    payments,
    payouts,
    tax,
    webhooks,
)

app = FastAPI(
    title="AgenticlyPay API",
    description="API for processing agentic payments (ACP, AP2, x402) via Stripe",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_url, "*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(connect.router, prefix="/api/v1/connect", tags=["Connect"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(payouts.router, prefix="/api/v1/payouts", tags=["Payouts"])
app.include_router(tax.router, prefix="/api/v1/tax", tags=["Tax"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AgenticlyPay API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

