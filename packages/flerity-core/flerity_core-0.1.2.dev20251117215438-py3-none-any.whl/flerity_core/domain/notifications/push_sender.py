"""Push notification sender via AWS SNS."""

import asyncio
import json
import re
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ...config import Config
from ...utils.logging import get_logger
from ...utils.enhanced_logging import log_push_error
from ...utils.tracing import trace_async

logger = get_logger(__name__)


class PushNotificationSender:
    """Send push notifications via AWS SNS."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.sns_client = boto3.client(
            'sns',
            region_name=getattr(self.config, 'AWS_REGION', 'us-east-1')
        )

        # Platform Application ARNs
        self.ios_arn = getattr(
            self.config,
            'AWS_SNS_PLATFORM_APPLICATION_ARN_IOS',
            'arn:aws:sns:us-east-1:955063685462:app/APNS/Flertify'
        )
        self.ios_sandbox_arn = getattr(
            self.config,
            'AWS_SNS_PLATFORM_APPLICATION_ARN_IOS_SANDBOX',
            None
        )
        self.android_arn = getattr(
            self.config,
            'AWS_SNS_PLATFORM_APPLICATION_ARN_ANDROID',
            None
        )

    @trace_async
    async def send_to_device(
        self,
        push_token: str,
        platform: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
        is_sandbox: bool = False
    ) -> tuple[bool, str | None]:
        """Send push notification to specific device.
        
        Returns:
            (success, error_message)
        """
        try:
            # Get platform ARN
            platform_arn = self._get_platform_arn(platform, is_sandbox)
            if not platform_arn:
                error_id = log_push_error(
                    error=ValueError(f"Platform ARN not configured for {platform}"),
                    operation="platform_arn_missing",
                    platform=platform,
                    is_sandbox=is_sandbox,
                    component="push_sender"
                )
                return False, f"Platform ARN not configured for {platform} (Error ID: {error_id})"

            # Create or get endpoint
            endpoint_arn = await self._create_platform_endpoint(
                platform_arn, push_token
            )

            if not endpoint_arn:
                error_id = log_push_error(
                    error=ValueError("Failed to create SNS endpoint"),
                    operation="create_sns_endpoint",
                    platform=platform,
                    push_token=push_token,
                    component="push_sender"
                )
                return False, f"Failed to create SNS endpoint (Error ID: {error_id})"

            # Build message payload
            message = self._build_message(platform, title, body, data)

            # Send via SNS
            response = await self._publish_to_endpoint(endpoint_arn, message)

            logger.info("Push notification sent", extra={
                "platform": platform,
                "endpoint_arn": endpoint_arn,
                "message_id": response.get('MessageId')
            })

            return True, None

        except (BotoCoreError, ClientError) as e:
            error_id = log_push_error(
                error=e,
                operation="send_notification",
                platform=platform,
                push_token=push_token,
                is_sandbox=is_sandbox,
                aws_service="SNS",
                component="push_sender"
            )
            error_msg = f"AWS SNS error (Error ID: {error_id}): {str(e)}"
            logger.error(error_msg, extra={
                "platform": platform,
                "error": str(e),
                "is_sandbox": is_sandbox,
                "error_id": error_id
            })
            return False, error_msg

        except Exception as e:
            error_id = log_push_error(
                error=e,
                operation="send_notification",
                platform=platform,
                push_token=push_token,
                component="push_sender"
            )
            error_msg = f"Push notification failed (Error ID: {error_id}): {str(e)}"
            logger.error(error_msg, extra={
                "platform": platform,
                "error": str(e),
                "error_id": error_id
            })
            return False, error_msg

    def _get_platform_arn(self, platform: str, is_sandbox: bool) -> str | None:
        """Get platform application ARN."""
        if platform == "ios":
            return self.ios_sandbox_arn if is_sandbox else self.ios_arn
        elif platform == "android":
            return self.android_arn
        return None

    async def _create_platform_endpoint(
        self, platform_arn: str, token: str
    ) -> str | None:
        """Create or retrieve SNS platform endpoint."""
        try:
            response = await asyncio.to_thread(
                self.sns_client.create_platform_endpoint,
                PlatformApplicationArn=platform_arn,
                Token=token
            )
            return response['EndpointArn']

        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidParameter':
                # Token already exists, extract from error message
                error_msg = e.response['Error']['Message']
                if 'Endpoint' in error_msg and 'already exists' in error_msg:
                    # Extract ARN from error message
                    match = re.search(r'arn:aws:sns:[^"]+', error_msg)
                    if match:
                        return match.group(0)

            error_id = log_push_error(
                error=e,
                operation="create_sns_endpoint",
                platform_arn=platform_arn,
                aws_error_code=e.response['Error']['Code'],
                component="push_sender"
            )
            logger.error(f"Failed to create SNS endpoint (Error ID: {error_id})", extra={
                "error": str(e),
                "platform_arn": platform_arn,
                "error_id": error_id,
                "aws_error_code": e.response['Error']['Code']
            })
            return None

    def _build_message(
        self,
        platform: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None
    ) -> str:
        """Build platform-specific message payload."""
        if platform == "ios":
            # APNS format
            apns_payload = {
                "aps": {
                    "alert": {
                        "title": title,
                        "body": body
                    },
                    "sound": "default",
                    "badge": 1
                }
            }
            if data:
                apns_payload.update(data)

            message = {
                "default": body,
                "APNS": json.dumps(apns_payload),
                "APNS_SANDBOX": json.dumps(apns_payload)
            }

        elif platform == "android":
            # FCM format
            fcm_payload = {
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data or {}
            }

            message = {
                "default": body,
                "GCM": json.dumps(fcm_payload)
            }
        else:
            message = {"default": body}

        return json.dumps(message)

    async def _publish_to_endpoint(
        self, endpoint_arn: str, message: str
    ) -> dict[str, Any]:
        """Publish message to SNS endpoint."""
        response = await asyncio.to_thread(
            self.sns_client.publish,
            TargetArn=endpoint_arn,
            Message=message,
            MessageStructure='json'
        )
        return response


def create_push_sender(config: Config | None = None) -> PushNotificationSender:
    """Factory function for push sender."""
    return PushNotificationSender(config)
