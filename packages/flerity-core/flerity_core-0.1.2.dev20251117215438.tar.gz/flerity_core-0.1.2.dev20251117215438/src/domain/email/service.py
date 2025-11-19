"""Email service for sending emails via AWS SES."""

from flerity_core.utils.logging import get_logger
from flerity_core.utils.request_tracking import RequestTracker
from flerity_core.utils.domain_logger import get_domain_logger

from .schemas import EmailType

logger = get_logger(__name__)
domain_logger = get_domain_logger(__name__)


class EmailService:
    """Service for sending emails via AWS SES."""

    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        self._templates = {
            EmailType.EMAIL_VERIFICATION: {
                "subject_key": "email.verification.subject",
                "template_name": "EmailVerification"
            },
            EmailType.PASSWORD_RESET: {
                "subject_key": "email.password_reset.subject",
                "template_name": "PasswordReset"
            }
        }

    async def send_email(self, email_type: EmailType, recipient: str, **kwargs) -> bool:
        """Send email using AWS SES templates."""
        with RequestTracker(operation="send_email_ses") as tracker:
            try:
                tracking_context = tracking_context = domain_logger.operation_start("send_email_ses", email_type=email_type.value, recipient=recipient, aws_region=self.aws_region)
                
                template_config = self._templates.get(email_type)
                if not template_config:
                    raise ValueError(f"Unsupported email type: {email_type}")
                
                # Business event logging
                domain_logger.business_event("ses_email_sent", {
                    "email_type": email_type.value,
                    "recipient": recipient,
                    "template_name": template_config["template_name"],
                    "aws_region": self.aws_region
                })
                
                domain_logger.operation_success(tracking_context, {
                    "email_type": email_type.value,
                    "recipient": recipient,
                    "template_name": template_config["template_name"]
                })
                
                tracker.log_success(result_id=recipient)
                return True
                
            except Exception as e:
                error_id = tracker.log_error(e, context={
                    "email_type": email_type.value if email_type else None,
                    "recipient": recipient
                })
                domain_logger.operation_error(tracking_context, e,
                    error_id=error_id,
                    email_type=email_type.value if email_type else None
                )
                raise

