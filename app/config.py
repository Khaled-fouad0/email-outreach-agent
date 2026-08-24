"""
Project Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reads secret API keys from the .env file.
If any required key is missing, the project automatically
falls back to "mock mode" (simulated AI responses, no real
API calls, no cost, no keys needed).
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    #~~~~~~~~~~~~~~SendGrid (for sending/receiving emails)~~~~~~~~~~~#
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "")

    #~~~~~~~~~~~~~~~~Groq (conversation logic - LLM)~~~~~~~~~~~~~~#
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    #~~~~~~~~~~~General settings~~~~~~~~~~~~~~~~~~~#
    APP_ENV: str = os.getenv("APP_ENV", "development")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8002")

    @property
    def is_mock_mode(self) -> bool:
        """
        If any required key is missing, run in mock mode
        (simulated responses instead of real API calls).
        """
        required_keys = [
            self.SENDGRID_API_KEY,
            self.SENDER_EMAIL,
            self.GROQ_API_KEY,
        ]
        return not all(required_keys)


settings = Settings()
