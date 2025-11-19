"""Email service for authentication notifications using SendGrid."""

from typing import Any

import httpx

from ..utils.config import email_config
from ..utils.errors import BadRequest, FailedDependency
from ..utils.i18n import t
from ..utils.logging import get_logger
from ..utils.request_tracking import RequestTracker
from ..utils.domain_logger import get_domain_logger

logger = get_logger(__name__)
domain_logger = get_domain_logger(__name__)

class EmailService:
    """Service for sending authentication-related emails via SendGrid."""

    def __init__(self) -> None:
        self.from_email = email_config.sendgrid_from_email
        self.api_key = email_config.sendgrid_api_key
        self.base_url = email_config.app_base_url

        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")

    def _validate_email(self, email: str) -> None:
        """Validate email format."""
        if not email or "@" not in email or len(email) > 254:
            raise BadRequest("Invalid email address")

    async def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """Send email via SendGrid API."""
        self._validate_email(to_email)

        if not subject.strip() or not (html_body.strip() or text_body.strip()):
            raise BadRequest("Email subject and body cannot be empty")

        payload: dict[str, Any] = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": subject
                }
            ],
            "from": {"email": self.from_email},
            "content": []
        }

        if text_body.strip():
            payload["content"].append({
                "type": "text/plain",
                "value": text_body
            })

        if html_body.strip():
            payload["content"].append({
                "type": "text/html",
                "value": html_body
            })

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code == 202:
                    logger.info("Email sent successfully", extra={"to_email": to_email, "subject": subject})
                    return True
                else:
                    error_message = response.text or f"HTTP {response.status_code}"
                    logger.error("SendGrid email failed", extra={
                        "to_email": to_email,
                        "status_code": response.status_code,
                        "error_message": error_message
                    })
                    raise FailedDependency(f"Email delivery failed: {error_message}")

        except httpx.RequestError as e:
            logger.error("SendGrid request error", extra={
                "to_email": to_email,
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            raise FailedDependency("Email service unavailable")
        except Exception as e:
            logger.error("Email service error", extra={
                "to_email": to_email,
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            raise FailedDependency("Email service unavailable")

    async def send_email_verification(self, email: str, verification_token: str, user_name: str | None = None, locale: str = "en-US") -> bool:
        """Send email verification email."""
        with RequestTracker(operation="send_email_verification") as tracker:
            try:
                tracking_context = domain_logger.operation_start("send_email_verification", email=email, has_token=bool(verification_token), user_name=user_name, locale=locale)
                
                if not verification_token.strip():
                    raise BadRequest("Verification token cannot be empty")

                verify_url = f"{self.base_url}/verify-email?token={verification_token}"
                display_name = user_name or email.split("@")[0]

                subject = t("email.verification.subject", locale=locale)

                html_body = f"""
                <h2>{t("email.verification.title", locale=locale)}</h2>
                <p>{t("email.verification.greeting", name=display_name, locale=locale)}</p>
                <p>{t("email.verification.instructions", locale=locale)}</p>
                <p><a href="{verify_url}" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">{t("email.verification.button", locale=locale)}</a></p>
                """

                text_body = f"""
                {t("email.verification.title", locale=locale)}
                
                {t("email.verification.greeting", name=display_name, locale=locale)}
                
                {t("email.verification.instructions", locale=locale)}
                
                {t("email.verification.link_text", locale=locale)}: {verify_url}
                """

                result = await self._send_email(email, subject, html_body, text_body)
                
                # Business event logging
                domain_logger.business_event("email_verification_sent", {
                    "email": email,
                    "user_name": user_name,
                    "locale": locale,
                    "success": result
                })
                
                domain_logger.operation_success(tracking_context, {
                    "email": email,
                    "success": result
                })
                
                tracker.log_success(result_id=email)
                return result
                
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "email": email,
                    "locale": locale
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "email": email
                })
                raise

    async def send_password_reset_email(self, email: str, reset_token: str, user_name: str | None = None, locale: str = "en-US") -> bool:
        """Send password reset email."""
        with RequestTracker(operation="send_password_reset_email") as tracker:
            try:
                tracking_context = domain_logger.operation_start("send_password_reset_email", email=email, has_token=bool(reset_token), user_name=user_name, locale=locale)
                
                if not reset_token.strip():
                    raise BadRequest("Reset token cannot be empty")

                display_name = user_name or email.split("@")[0]

                subject = t("email.password_reset.subject", locale=locale)

                html_body = f"""
                <h2>{t("email.password_reset.title", locale=locale)}</h2>
                <p>{t("email.password_reset.greeting", name=display_name, locale=locale)}</p>
                <p>{t("email.password_reset.instructions", locale=locale)}</p>
                <div style="text-align: center; margin: 20px 0;">
                    <div style="font-size: 24px; font-weight: bold; letter-spacing: 2px; color: #007bff; background: #f8f9fa; padding: 15px; border-radius: 8px; display: inline-block;">
                        {reset_token}
                    </div>
                </div>
                <p><small>{t("email.password_reset.expires", locale=locale)}</small></p>
                """

                text_body = f"""
                {t("email.password_reset.title", locale=locale)}
                
                {t("email.password_reset.greeting", name=display_name, locale=locale)}
                
                {t("email.password_reset.instructions", locale=locale)}
                
                {t("email.password_reset.code_text", locale=locale)}: {reset_token}
                
                {t("email.password_reset.expires", locale=locale)}
                """

                result = await self._send_email(email, subject, html_body, text_body)
                
                # Business event logging
                domain_logger.business_event("password_reset_email_sent", {
                    "email": email,
                    "user_name": user_name,
                    "locale": locale,
                    "success": result
                })
                
                domain_logger.operation_success(tracking_context, {
                    "email": email,
                    "success": result
                })
                
                tracker.log_success(result_id=email)
                return result
                
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "email": email,
                    "locale": locale
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "email": email
                })
                raise

    async def send_welcome_email(self, email: str, user_name: str | None = None, locale: str = "en-US") -> bool:
        """Send welcome email to new users."""
        with RequestTracker(operation="send_welcome_email") as tracker:
            try:
                tracking_context = domain_logger.operation_start("send_welcome_email", email=email, user_name=user_name, locale=locale)
                
                display_name = user_name or email.split("@")[0]
                app_url = self.base_url

                subject = t("email.welcome.subject", locale=locale)

                html_body = f"""
                <h2>{t("email.welcome.title", locale=locale)}</h2>
                <p>{t("email.welcome.greeting", name=display_name, locale=locale)}</p>
                <p>{t("email.welcome.message", locale=locale)}</p>
                <p><a href="{app_url}" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">{t("email.welcome.button", locale=locale)}</a></p>
                """

                text_body = f"""
                {t("email.welcome.title", locale=locale)}
                
                {t("email.welcome.greeting", name=display_name, locale=locale)}
                
                {t("email.welcome.message", locale=locale)}
                
                {t("email.welcome.link_text", locale=locale)}: {app_url}
                """

                result = await self._send_email(email, subject, html_body, text_body)
                
                # Business event logging
                domain_logger.business_event("welcome_email_sent", {
                    "email": email,
                    "user_name": user_name,
                    "locale": locale,
                    "success": result
                })
                
                domain_logger.operation_success(tracking_context, {
                    "email": email,
                    "success": result
                })
                
                tracker.log_success(result_id=email)
                return result
                
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "email": email,
                    "locale": locale
                })
                domain_logger.operation_error(tracking_context, str(e), {
                    "error_id": error_id,
                    "email": email
                })
                raise
