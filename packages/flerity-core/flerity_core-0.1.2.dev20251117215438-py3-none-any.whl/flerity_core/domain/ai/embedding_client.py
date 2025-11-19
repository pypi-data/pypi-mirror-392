"""Embedding client for Amazon Titan Embeddings G1."""

import json
from typing import Any

import boto3
from botocore.config import Config

from flerity_core.utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingClient:
    """Client for generating embeddings using Amazon Titan Embeddings G1."""

    MODEL_ID = "amazon.titan-embed-text-v1"
    DIMENSIONS = 1536

    def __init__(self, region: str = "us-east-1"):
        """Initialize Bedrock client for embeddings."""
        config = Config(
            region_name=region,
            retries={"max_attempts": 3, "mode": "adaptive"}
        )
        self.client = boto3.client("bedrock-runtime", config=config)
        self.region = region

    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed (max 8192 tokens)
            
        Returns:
            List of 1536 floats representing the embedding
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Truncate if too long (rough estimate: 1 token ≈ 4 chars)
        max_chars = 8192 * 4
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning("Text truncated for embedding", extra={
                "original_length": len(text),
                "truncated_length": max_chars
            })

        try:
            body = json.dumps({"inputText": text})
            
            response = self.client.invoke_model(
                modelId=self.MODEL_ID,
                body=body,
                contentType="application/json",
                accept="application/json"
            )

            response_body = json.loads(response["body"].read())
            embedding = response_body.get("embedding")

            if not embedding or len(embedding) != self.DIMENSIONS:
                raise ValueError(f"Invalid embedding dimensions: {len(embedding) if embedding else 0}")

            logger.debug("Embedding generated", extra={
                "text_length": len(text),
                "dimensions": len(embedding)
            })

            return embedding

        except Exception as e:
            logger.error("Failed to generate embedding", extra={
                "error": str(e),
                "text_length": len(text)
            })
            raise

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (each is a list of 1536 floats)
        """
        if not texts:
            return []

        embeddings = []
        for text in texts:
            try:
                embedding = await self.embed(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error("Failed to embed text in batch", extra={
                    "error": str(e),
                    "text_preview": text[:100]
                })
                # Return zero vector on failure
                embeddings.append([0.0] * self.DIMENSIONS)

        return embeddings
