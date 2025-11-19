"""Email domain schemas."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr


class EmailType(str, Enum):
    """Email template types."""
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class EmailRequest(BaseModel):
    """Email sending request."""
    to_email: EmailStr
    email_type: EmailType
    user_id: str
    locale: str = "en-US"
    template_data: dict[str, Any] = {}



