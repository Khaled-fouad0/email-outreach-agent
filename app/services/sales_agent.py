"""
Sales Agent Service (Email)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
has two jobs:

1) Generate a cold outreach email to a new potential lead
2) Reply intelligently when a lead responds to that email

Two modes:
1) Mock Mode:replies without API keys
2) Real Mode: uses Groq (Llama 3) to generate personalized emails
"""

from app.config import settings

SYSTEM_PROMPT = """
You are a professional, friendly sales representative for a software
company, writing outreach and follow-up emails to potential customers.

Your job:
1. Write concise, professional emails (not pushy or spammy)
2. Personalize based on any information given about the lead
3. Keep a clear call-to-action (book a call, reply with questions, etc.)
4. Keep emails short: 3-5 sentences max, plus a greeting and sign-off

IMPORTANT: Always reply in the same language the lead used in their
last message. If they wrote in Arabic, reply fully in Arabic (Egyptian
dialect). If they wrote in English, reply fully in English.
Never mix two languages in the same email.
"""


class SalesAgent:
    def __init__(self):
        self.conversation_history: list[dict] = []
        self.mock_mode = settings.is_mock_mode

    def generate_outreach_email(self, lead_name: str, lead_company: str = "") -> dict:
        """
        Generates the FIRST email sent to a new lead (cold outreach).
        Returns a dict with 'subject' and 'body'.
        """
        if self.mock_mode:
            subject = f"Quick question about {lead_company or 'your business'}"
            body = (
                f"Hi {lead_name},\n\n"
                f"I noticed your company might benefit from AI automation "
                f"tools that save time on repetitive tasks. Would you be "
                f"open to a quick 15-minute call this week to explore if "
                f"it's a good fit?\n\n"
                f"Best,\nAI Sales Agent"
            )
        else:
            prompt = (
                f"Write a cold outreach email to {lead_name}"
                f"{f' at {lead_company}' if lead_company else ''} "
                f"introducing our AI automation software. Keep it short and friendly."
            )
            subject, body = self._real_groq_email(prompt)

        self.conversation_history.append({"role": "assistant", "content": body})
        return {"subject": subject, "body": body}

    def _mock_reply(self, user_text: str) -> str:
        """reply without real API keys."""
        text = user_text.lower()

        price_keywords = ["سعر", "تكلفة", "price", "cost"]
        booking_keywords = ["موعد", "احجز", "appointment", "book", "call"]
        rejection_keywords = ["لا", "مش عايز", "no", "not interested"]

        if any(word in text for word in price_keywords):
            return "Our basic plan starts at $99/month. Would you like me to send over a detailed breakdown?"
        elif any(word in text for word in booking_keywords):
            return "Great! What day and time works best for a quick call?"
        elif any(word in text for word in rejection_keywords):
            return "No problem at all, thanks for your time! Feel free to reach out anytime."
        else:
            return "Thanks for your reply! We provide AI automation solutions that save your company time and money. Want to hear more details?"

    def get_response(self, user_text: str) -> str:
        """Main entry point:
        takes lead's reply email, returns agent's reply body."""
        self.conversation_history.append({"role": "user", "content": user_text})

        if self.mock_mode:
            reply = self._mock_reply(user_text)
        else:
            reply = self._real_groq_reply(user_text)

        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def _real_groq_reply(self, user_text: str) -> str:
        """Real mode:
        generates a reply to an incoming email using Groq."""
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=200,
        )
        return response.choices[0].message.content

    def _real_groq_email(self, prompt: str) -> tuple[str, str]:
        """Real mode:
        generates a fresh outreach email (subject + body) using Groq."""
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{prompt}\n\nRespond in this exact format:\nSUBJECT: <subject line>\nBODY: <email body>"},
        ]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=250,
        )
        content = response.choices[0].message.content

        subject = "Quick question for you"
        body = content
        if "SUBJECT:" in content and "BODY:" in content:
            parts = content.split("BODY:")
            subject = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()

        return subject, body
