"""AWS Bedrock client for Amazon Nova Lite integration."""

import asyncio
import base64
import os

import aioboto3

from flerity_core.utils.logging import get_logger
from flerity_core.utils.request_tracking import RequestTracker
from flerity_core.utils.domain_logger import get_domain_logger

from .schemas import AIProviderError, AIProviderRateLimit, AIProviderTimeout

logger = get_logger(__name__)
domain_logger = get_domain_logger("ai.bedrock")


class BedrockClient:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.session = aioboto3.Session()
        # Use fine-tuned model for Portuguese Brazilian
        self.primary_model = os.getenv("AI_CUSTOM_MODEL_ARN", "amazon.nova-lite-v1:0")
        self.fallback_model = os.getenv("AI_FALLBACK_MODEL", "amazon.nova-micro-v1:0")

    async def generate_text(
        self,
        prompt: str,
        model_id: str | None = None,
        max_tokens: int = 1000,
        timeout: float | None = None,
        use_custom_model: bool = True,
        image_url: str | None = None
    ) -> str:
        """Generate text using AWS Bedrock with fine-tuned Amazon Nova Lite.
        
        Args:
            prompt: Text prompt
            model_id: Model ID to use
            max_tokens: Maximum tokens to generate
            timeout: Timeout in seconds
            use_custom_model: Whether to use custom fine-tuned model
            image_url: Optional image URL for multimodal generation
        """
        with RequestTracker(operation="generate_text", model_id=model_id, 
                          use_custom_model=use_custom_model, has_image=bool(image_url)) as tracker:
            try:
                tracking_context = domain_logger.operation_start("generate_text", 
                    model_id=model_id, max_tokens=max_tokens, use_custom_model=use_custom_model,
                    has_image=bool(image_url), prompt_length=len(prompt))

                # Use environment timeout if not provided
                if timeout is None:
                    timeout_ms = int(os.getenv("AI_SYNC_TIMEOUT_MS", "30000"))  # 30 seconds default
                    timeout = timeout_ms / 1000.0

                # Use custom model by default
                if use_custom_model and model_id is None:
                    model_id = self.primary_model
                elif model_id is None:
                    model_id = "amazon.nova-lite-v1:0"

                async with self.session.client("bedrock-runtime", region_name=self.region) as client:
                    # Prepare request for Amazon Nova Lite
                    if "amazon.nova" in model_id:
                        # Build content array (text + optional image)
                        content = []
                        
                        # Add image first if provided (better for vision models)
                        if image_url:
                            # Check if it's a data URL (base64)
                            if image_url.startswith('data:'):
                                # Extract format and base64 data
                                # Format: data:image/jpeg;base64,{base64_string}
                                parts = image_url.split(',', 1)
                                if len(parts) == 2:
                                    header = parts[0]  # data:image/jpeg;base64
                                    base64_string = parts[1]
                                    
                                    # Extract format from header
                                    format_part = header.split(';')[0].split('/')[-1]  # jpeg, png, etc
                                    
                                    # Decode base64 to bytes
                                    try:
                                        image_bytes = base64.b64decode(base64_string)
                                    except Exception as e:
                                        error_id = domain_logger.operation_error(tracking_context, 
                                            error=AIProviderError(f"Invalid base64 image data: {str(e)}"),
                                            model_id=model_id, image_format=format_part)
                                        raise AIProviderError(f"Invalid base64 image data: {str(e)}")
                                    
                                    content.append({
                                        "image": {
                                            "format": format_part,
                                            "source": {
                                                "bytes": image_bytes  # Nova needs actual bytes, not base64 string
                                            }
                                        }
                                    })
                            else:
                                # Regular URL
                                # Infer format from URL extension
                                format_ext = "jpeg"
                                if image_url.endswith('.png'):
                                    format_ext = "png"
                                elif image_url.endswith('.gif'):
                                    format_ext = "gif"
                                elif image_url.endswith('.webp'):
                                    format_ext = "webp"
                                
                                content.append({
                                    "image": {
                                        "format": format_ext,
                                        "source": {
                                            "url": image_url
                                        }
                                    }
                                })
                        
                        # Add text prompt
                        content.append({"text": prompt})
                        
                        body = {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": content
                                }
                            ],
                            "inferenceConfig": {
                                "maxTokens": max_tokens,
                                "temperature": 0.7,
                                "topP": 0.9
                            }
                        }
                    else:
                        error_id = domain_logger.operation_error(tracking_context, 
                            error=AIProviderError(f"Unsupported model: {model_id}"),
                            model_id=model_id)
                        raise AIProviderError(f"Unsupported model: {model_id}")

                    try:
                        domain_logger.external_api_call("bedrock", "converse", 
                            method="POST", model_id=model_id, max_tokens=max_tokens, timeout=timeout)
                        
                        response = await asyncio.wait_for(
                            client.converse(
                                modelId=model_id,
                                messages=body["messages"],
                                inferenceConfig=body["inferenceConfig"]
                            ),
                            timeout=timeout
                        )

                        # Parse Nova response
                        result_text = str(response['output']['message']['content'][0]['text'])
                        
                        domain_logger.business_event("bedrock_text_generated", 
                            model_id=model_id, prompt_length=len(prompt), 
                            response_length=len(result_text), use_custom_model=use_custom_model)
                        domain_logger.operation_success(tracking_context, 
                            model_id=model_id, prompt_length=len(prompt), 
                            response_length=len(result_text), timeout=timeout)
                        tracker.log_success(response_length=len(result_text), model_used=model_id)
                        return result_text

                    except TimeoutError:
                        # Fallback to alternative model if timeout
                        if use_custom_model and model_id != "amazon.nova-lite-v1:0":
                            domain_logger.business_event("bedrock_fallback_to_base_model", 
                                original_model=model_id, fallback_model="amazon.nova-lite-v1:0")
                            logger.warning("Custom model timeout, falling back to base model")
                            return await self.generate_text(
                                prompt,
                                model_id="amazon.nova-lite-v1:0",
                                max_tokens=max_tokens,
                                timeout=timeout,
                                use_custom_model=False
                            )
                        error_id = domain_logger.operation_error(tracking_context, 
                            error=AIProviderTimeout("Bedrock request timed out"),
                            model_id=model_id, timeout=timeout)
                        raise AIProviderTimeout("Bedrock request timed out")
                    except Exception as e:
                        if "ThrottlingException" in str(e):
                            error_id = domain_logger.operation_error(tracking_context, 
                                error=AIProviderRateLimit("Bedrock rate limit exceeded"),
                                model_id=model_id, error_type="throttling")
                            raise AIProviderRateLimit("Bedrock rate limit exceeded")
                        error_id = domain_logger.operation_error(tracking_context, 
                            error=AIProviderError(f"Bedrock error: {str(e)}"),
                            model_id=model_id, error_type=type(e).__name__)
                        raise AIProviderError(f"Bedrock error: {str(e)}")
            except (AIProviderError, AIProviderRateLimit, AIProviderTimeout):
                raise
            except Exception as e:
                error_id = domain_logger.operation_error(tracking_context, error=e,
                    model_id=model_id, use_custom_model=use_custom_model)
                tracker.log_error(e, context={"model_id": model_id, "use_custom_model": use_custom_model})
                raise

    async def check_custom_model_status(self) -> dict:
        """Check status of custom fine-tuned model."""
        with RequestTracker(operation="check_custom_model_status", model_arn=self.primary_model) as tracker:
            try:
                tracking_context = domain_logger.operation_start("check_custom_model_status", model_arn=self.primary_model)
                
                async with self.session.client("bedrock", region_name=self.region) as client:
                    try:
                        domain_logger.external_api_call("bedrock", "get_model_customization_job", 
                            method="GET", model_arn=self.primary_model)
                        
                        response = await client.get_model_customization_job(
                            jobIdentifier=self.primary_model.split('/')[-1]
                        )
                        
                        result = {
                            "status": response.get("status"),
                            "model_arn": response.get("outputModelArn"),
                            "training_metrics": response.get("trainingMetrics", {})
                        }
                        
                        domain_logger.business_event("custom_model_status_checked", 
                            model_arn=self.primary_model, status=result["status"])
                        domain_logger.operation_success(tracking_context, 
                            model_arn=self.primary_model, status=result["status"])
                        tracker.log_success(status=result["status"], model_arn=result.get("model_arn"))
                        return result
                    except Exception as e:
                        error_id = domain_logger.operation_error(tracking_context, error=e,
                            model_arn=self.primary_model)
                        result = {"status": "unknown", "error": str(e)}
                        tracker.log_error(e, context={"model_arn": self.primary_model})
                        return result
            except Exception as e:
                error_id = domain_logger.operation_error(tracking_context, error=e,
                    model_arn=self.primary_model)
                tracker.log_error(e, context={"model_arn": self.primary_model})
                return {"status": "error", "error": str(e)}
