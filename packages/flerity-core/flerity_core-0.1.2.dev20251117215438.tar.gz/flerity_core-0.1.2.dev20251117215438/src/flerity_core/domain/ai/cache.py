"""
Intelligent prompt caching with semantic similarity matching.
"""
import base64
import hashlib
import json
from datetime import datetime
from typing import Any

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

    class MockNumpy:
        ndarray = Any
        @staticmethod
        def frombuffer(*args: Any, **kwargs: Any) -> list[float]: return [0.0] * 384

    np = MockNumpy()

from pydantic import BaseModel
from redis.asyncio import Redis

try:
    from flerity_core.domain.ai.embeddings import EmbeddingService
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

    class MockEmbeddingService:
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        async def get_embeddings(self, texts: list[str]) -> list[list[float]]: return [[0.0] * 384 for _ in texts]
        def calculate_similarity(self, _emb1: Any, _emb2: Any) -> float: return 0.0

    EmbeddingService = MockEmbeddingService  # type: ignore[assignment,misc]

from flerity_core.utils.clock import utcnow
from flerity_core.utils.logging import get_logger

logger = get_logger(__name__)


class AICache:
    """Simple Redis cache for AI responses."""
    
    def __init__(self, redis_client: Redis | None = None, ttl: int = 21600):
        """Initialize cache with Redis client and TTL (default 6 hours)."""
        self.redis = redis_client
        self.ttl = ttl
        self.enabled = redis_client is not None
    
    async def get(self, key: str) -> dict | None:
        """Get cached value by key."""
        if not self.enabled:
            return None
        try:
            cached = await self.redis.get(f"ai:cache:{key}")
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.warning(f"Cache get failed for {key}: {e}")
            return None
    
    async def set(self, key: str, value: dict, ttl: int | None = None) -> None:
        """Set cached value with TTL."""
        if not self.enabled:
            return
        try:
            ttl = ttl or self.ttl
            await self.redis.setex(
                f"ai:cache:{key}",
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")


class CachedResponse(BaseModel):
    """Cached AI response with metadata."""
    response: str
    similarity: float
    cached_at: datetime
    metadata: dict = {}


class PromptCache:
    """Intelligent cache for AI prompts using semantic similarity."""

    def __init__(
        self,
        redis_client: Redis,
        embedding_service: EmbeddingService,
        cache_ttl: int = 300,  # 5 minutes
        similarity_threshold: float = 0.95
    ):
        self.redis = redis_client
        self.embedding_service = embedding_service
        self.cache_ttl = cache_ttl
        self.similarity_threshold = similarity_threshold

    async def get_cached_response(self, prompt: str, context_hash: str) -> CachedResponse | None:
        """Try to find similar cached prompt response."""
        # 1. Check exact match first
        exact_key = f"ai:cache:exact:{self._hash_prompt(prompt)}"
        cached = await self.redis.get(exact_key)
        if cached:
            data = json.loads(cached)
            return CachedResponse(**data, similarity=1.0)

        # 2. Semantic similarity search
        return await self._semantic_search(prompt, context_hash)

    async def cache_response(
        self,
        prompt: str,
        response: str,
        context_hash: str,
        metadata: dict[Any, Any] | None = None
    ) -> None:
        """Cache prompt-response pair with embedding for semantic search."""
        prompt_hash = self._hash_prompt(prompt)
        metadata = metadata or {}

        # Generate embedding for semantic search
        prompt_embedding = await self.embedding_service.get_embeddings([prompt])

        cache_data = CachedResponse(
            response=response,
            similarity=1.0,
            cached_at=utcnow(),
            metadata=metadata
        )

        # Store exact match
        exact_key = f"ai:cache:exact:{prompt_hash}"
        await self.redis.setex(exact_key, self.cache_ttl, cache_data.model_dump_json())

        # Store for semantic search
        semantic_key = f"ai:cache:semantic:{prompt_hash}"
        semantic_data: dict[str, str] = {
            'response': response,
            'embedding': base64.b64encode(prompt_embedding[0].tobytes()).decode(),
            'cached_at': utcnow().isoformat(),
            'metadata': json.dumps(metadata)
        }
        await self.redis.hset(semantic_key, mapping=semantic_data)
        await self.redis.expire(semantic_key, self.cache_ttl)

        # Add to context index for faster lookup
        context_key = f"ai:cache:context:{context_hash}"
        await self.redis.sadd(context_key, semantic_key)
        await self.redis.expire(context_key, self.cache_ttl)

        logger.debug(f"Cached prompt response: {prompt_hash[:8]}...")

    async def _semantic_search(self, prompt: str, context_hash: str) -> CachedResponse | None:
        """Search for semantically similar cached prompts."""
        # Get recent cache keys for this context
        context_key = f"ai:cache:context:{context_hash}"
        recent_keys = await self.redis.smembers(context_key)

        if not recent_keys:
            return None

        # Generate embedding for search prompt
        prompt_embedding = await self.embedding_service.get_embeddings([prompt])
        search_embedding = prompt_embedding[0]

        best_match = None
        best_similarity = 0.0

        for cache_key in recent_keys:
            cached_data = await self.redis.hgetall(cache_key)
            if not cached_data:
                continue

            try:
                # Decode cached embedding
                cached_embedding = np.frombuffer(
                    base64.b64decode(cached_data['embedding']),
                    dtype=np.float32
                )

                # Calculate similarity
                similarity = self.embedding_service.calculate_similarity(
                    search_embedding,
                    cached_embedding
                )

                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = CachedResponse(
                        response=cached_data['response'],
                        similarity=similarity,
                        cached_at=datetime.fromisoformat(cached_data['cached_at']),
                        metadata=json.loads(cached_data.get('metadata', '{}'))
                    )
            except Exception as e:
                logger.warning(f"Error processing cached embedding: {e}")
                continue

        if best_match:
            logger.info(f"Cache hit with similarity: {best_similarity:.3f}")

        return best_match

    async def invalidate_context(self, context_hash: str) -> int:
        """Invalidate all cached entries for a context."""
        context_key = f"ai:cache:context:{context_hash}"
        cache_keys = await self.redis.smembers(context_key)

        if not cache_keys:
            return 0

        # Delete all semantic cache entries
        deleted = await self.redis.delete(*cache_keys)

        # Delete context index
        await self.redis.delete(context_key)

        logger.info(f"Invalidated {deleted} cache entries for context {context_hash[:8]}...")
        return deleted

    async def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        # Count cache entries by type
        exact_pattern = "ai:cache:exact:*"
        semantic_pattern = "ai:cache:semantic:*"

        exact_keys = []
        semantic_keys = []

        async for key in self.redis.scan_iter(match=exact_pattern):
            exact_keys.append(key)

        async for key in self.redis.scan_iter(match=semantic_pattern):
            semantic_keys.append(key)

        return {
            "exact_entries": len(exact_keys),
            "semantic_entries": len(semantic_keys),
            "total_entries": len(exact_keys) + len(semantic_keys),
            "ttl_seconds": self.cache_ttl,
            "similarity_threshold": self.similarity_threshold
        }

    def _hash_prompt(self, prompt: str) -> str:
        """Generate hash for prompt."""
        return hashlib.sha256(prompt.encode()).hexdigest()
