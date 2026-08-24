"""
Email Routes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Two different endpoints for two different jobs:

1) /email/send-outreach -> triggered manually (or by a script) to send
                            the FIRST email to a new lead
2) /email/webhook        -> triggered automatically by SendGrid's Inbound
                            Parse whenever a lead replies to our email
"""

from fastapi import APIRouter, Form
from pydantic import BaseModel

from app.services.sales_agent import SalesAgent
from app.services.email_sender import send_email

router = APIRouter(prefix="/email", tags=["email"])

# Temporary in-memory storage for active conversations
# (in real production this should be replaced with Redis or a database)
active_sessions: dict[str, SalesAgent] = {}


class OutreachRequest(BaseModel):
    lead_email: str
    lead_name: str
    lead_company: str = ""


@router.post("/send-outreach")
async def send_outreach(request: OutreachRequest):
    """
    Starts a new outreach conversation: generates a personalized first
    email using the agent, sends it via SendGrid, and creates a new
    session so we can track the reply later.
    """
    agent = SalesAgent()
    active_sessions[request.lead_email] = agent

    email_content = agent.generate_outreach_email(
        lead_name=request.lead_name,
        lead_company=request.lead_company,
    )

    send_email(
        to_email=request.lead_email,
        subject=email_content["subject"],
        body=email_content["body"],
    )

    return {
        "status": "sent",
        "to": request.lead_email,
        "subject": email_content["subject"],
    }


@router.post("/webhook")
async def email_webhook(
    from_email: str = Form(..., alias="from"),
    subject: str = Form(""),
    text: str = Form(""),
):
    """
    Triggered by SendGrid's Inbound Parse whenever a lead replies.
    SendGrid sends the sender's email, subject, and plain-text body.
    """
    agent = active_sessions.get(from_email)
    if agent is None:
        agent = SalesAgent()
        active_sessions[from_email] = agent

    reply_text = agent.get_response(text)

    send_email(
        to_email=from_email,
        subject=f"Re: {subject}",
        body=reply_text,
    )

    return {"status": "replied", "to": from_email}
