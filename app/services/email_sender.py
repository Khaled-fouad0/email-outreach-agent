"""
Email Sender Service
======================
Handles the actual sending of emails via SendGrid's API.
Kept separate from the routes and the agent logic, so if we ever
switch email providers, we only need to change this one file.
"""

from app.config import settings


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends an email via SendGrid. In mock mode, just prints to the
    console instead of making a real API call (no cost, no keys needed).
    """
    if settings.is_mock_mode:
        print(f"[MOCK EMAIL] To: {to_email}")
        print(f"[MOCK EMAIL] Subject: {subject}")
        print(f"[MOCK EMAIL] Body: {body}")
        return True

    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=settings.SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    response = sg.send(message)

    return response.status_code in (200, 201, 202)