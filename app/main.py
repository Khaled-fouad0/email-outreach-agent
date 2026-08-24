"""
Main Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is where everything comes together and the server starts.
"""

from fastapi import FastAPI
from app.routes import email
from app.config import settings

app = FastAPI(
    title="Email Outreach Agent",
    description="AI-powered email outreach agent built with SendGrid + Groq",
    version="1.0.0",
)

app.include_router(email.router)


@app.get("/")
async def root():
    """Simple health-check endpoint to confirm the server is running."""
    return {
        "status": "running",
        "service": "Email Outreach Agent",
        "mode": "mock" if settings.is_mock_mode else "production",
    }


@app.get("/health")
async def health_check():
    """Used by Docker/hosting platforms to verify the server is alive."""
    return {"status": "healthy"}
