"""Content moderation pipeline for AI module."""

import re

from pydantic import BaseModel

from flerity_core.utils.errors import BadRequest
from flerity_core.utils.logging import get_logger

from .blocklist_repository import BlocklistRepository
from .schemas import UserLocale

logger = get_logger(__name__)


class ModerationResult(BaseModel):
    """Result of content moderation."""
    sanitized_text: str
    flags: list[str]
    pii_found: list[str] = []
    blocked_terms: list[str] = []
    toxicity_score: float | None = None
    safety_score: float | None = None
    quality_score: float | None = None

    @property
    def is_safe(self) -> bool:
        """Check if content is safe (no flags)."""
        return len(self.flags) == 0


class AIContentFlagged(BadRequest):
    """Content flagged by moderation."""
    def __init__(self, message: str, flags: list[str] | None = None):
        super().__init__(message)
        self.flags = flags or []


class ModerationService:
    """Content moderation service for AI inputs and outputs."""

    def __init__(self, blocklist_repo: BlocklistRepository | None = None):
        self.blocklist_repo = blocklist_repo
        self.pii_patterns = self._load_pii_patterns()
        self._blocklist_cache: dict[str, list[str]] = {}

    async def moderate_input(self, text: str, locale: UserLocale, context: dict[str, str] | None = None) -> ModerationResult:
        """Moderate input before sending to LLM."""
        flags = []
        sanitized_text = text

        # 1. PII Detection & Sanitization
        pii_found = self._detect_pii(text)
        if pii_found:
            flags.append("pii_detected")
            sanitized_text = self._sanitize_pii(text)

        # 2. Blocklist Check (language-aware)
        blocked_terms = await self._check_blocklist(text, locale.language)
        if blocked_terms:
            flags.append("blocked_terms")
            raise AIContentFlagged("Content contains blocked terms", flags)

        # 3. Content Classification (basic)
        toxicity_score = await self._classify_toxicity(text, locale.language)
        if toxicity_score > 0.8:
            flags.append("high_toxicity")
            raise AIContentFlagged("Content flagged as potentially toxic", flags)

        return ModerationResult(
            sanitized_text=sanitized_text,
            flags=flags,
            pii_found=pii_found,
            blocked_terms=blocked_terms,
            toxicity_score=toxicity_score
        )

    async def moderate_output(self, text: str, locale: UserLocale, context: dict[str, str] | None = None) -> ModerationResult:
        """Moderate LLM output before returning to user."""
        flags = []

        # 1. Output Safety Check
        safety_score = await self._classify_safety(text, locale.language)
        if safety_score < 0.7:
            flags.append("unsafe_output")
            raise AIContentFlagged("Generated content flagged as unsafe", flags)

        # 2. Quality Check
        quality_score = self._assess_quality(text)
        if quality_score < 0.5:
            flags.append("low_quality")

        return ModerationResult(
            sanitized_text=text,
            flags=flags,
            safety_score=safety_score,
            quality_score=quality_score
        )

    async def _check_blocklist(self, text: str, language: str) -> list[str]:
        """Check for blocked terms in user's language."""
        if not self.blocklist_repo:
            return []
        
        # Get cached blocklist or fetch from database
        if language not in self._blocklist_cache:
            terms = await self.blocklist_repo.get_active_terms(language)
            self._blocklist_cache[language] = [term.term for term in terms]

        text_lower = text.lower()
        found = []

        for term in self._blocklist_cache[language]:
            if term in text_lower:
                found.append(term)

        return found

    async def _classify_toxicity(self, text: str, language: str) -> float:
        """Language-aware toxicity classification."""
        if not self.blocklist_repo:
            return 0.0
        
        # Get inappropriate terms for this language
        inappropriate_terms = await self.blocklist_repo.get_terms_by_category(
            language, "inappropriate"
        )

        text_lower = text.lower()
        toxic_count = sum(1 for term in inappropriate_terms if term.term in text_lower)

        # Normalize to 0-1 scale
        return min(toxic_count / max(len(inappropriate_terms), 1), 1.0)

    async def _classify_safety(self, text: str, language: str) -> float:
        """Language-aware safety classification for outputs."""
        if not self.blocklist_repo:
            return 1.0  # Assume safe if no blocklist available
        
        # Get scam/personal_info terms for this language
        unsafe_terms = await self.blocklist_repo.get_terms_by_category(
            language, "scam"
        )
        personal_info_terms = await self.blocklist_repo.get_terms_by_category(
            language, "personal_info"
        )

        all_unsafe = unsafe_terms + personal_info_terms
        text_lower = text.lower()

        unsafe_count = sum(1 for term in all_unsafe if term.term in text_lower)

        # Higher score = safer (inverted from toxicity)
        return max(1.0 - (unsafe_count / max(len(all_unsafe), 1)), 0.0)

    def _detect_pii(self, text: str) -> list[str]:
        """Detect PII patterns (language-agnostic)."""
        found = []
        for pattern_name, regex in self.pii_patterns.items():
            if regex.search(text):
                found.append(pattern_name)
        return found

    def _sanitize_pii(self, text: str) -> str:
        """Replace PII with placeholders (language-agnostic)."""
        sanitized = text
        for pattern_name, regex in self.pii_patterns.items():
            placeholder = f"[{pattern_name.upper()}]"
            sanitized = regex.sub(placeholder, sanitized)
        return sanitized

    def _assess_quality(self, text: str) -> float:
        """Basic quality assessment (language-agnostic)."""
        if len(text.strip()) < 10:
            return 0.2  # Too short

        if len(text) > 500:
            return 0.3  # Too long

        # Check for coherence indicators
        has_punctuation = any(p in text for p in ".!?")
        has_proper_case = text[0].isupper() if text else False

        quality = 0.5
        if has_punctuation:
            quality += 0.2
        if has_proper_case:
            quality += 0.2

        return min(quality, 1.0)

    def _load_pii_patterns(self) -> dict[str, re.Pattern]:
        """Load PII detection patterns (language-agnostic)."""
        return {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{2,3}[-.\s]?\d{4,5}[-.\s]?\d{4}\b'),  # Brazilian phone patterns
            "cpf": re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'),
            "credit_card": re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            "url": re.compile(r'https?://[^\s]+'),
        }

    async def refresh_blocklist_cache(self, language: str | None = None) -> None:
        """Refresh blocklist cache for a language or all languages."""
        if language:
            if language in self._blocklist_cache:
                del self._blocklist_cache[language]
        else:
            self._blocklist_cache.clear()

        logger.info(f"Blocklist cache refreshed for language: {language or 'all'}")
