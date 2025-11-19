"""Internationalization utilities."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# Supported locales
SUPPORTED_LOCALES = ["en-US", "es-ES", "pt-BR"]
DEFAULT_LOCALE = "en-US"

# Translation cache
_TRANSLATIONS: dict[str, dict[str, str]] = {}


@dataclass
class UserLocale:
    """User locale information."""
    locale: str = DEFAULT_LOCALE
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        """Validate locale."""
        if self.locale not in SUPPORTED_LOCALES:
            self.locale = DEFAULT_LOCALE


def _load_translations() -> dict[str, dict[str, str]]:
    """Load translations from locale files."""
    if _TRANSLATIONS:
        return _TRANSLATIONS

    # Get the locales directory path
    locales_dir = Path(__file__).parent.parent / "locales"

    for locale in SUPPORTED_LOCALES:
        locale_file = locales_dir / f"{locale}.json"

        if locale_file.exists():
            try:
                with open(locale_file, encoding='utf-8') as f:
                    _TRANSLATIONS[locale] = json.load(f)
                logger.debug(f"Loaded translations for {locale}")
            except Exception as e:
                logger.warning(f"Failed to load translations for {locale}: {e}")
                _TRANSLATIONS[locale] = {}
        else:
            logger.debug(f"No translation file found for {locale}")
            _TRANSLATIONS[locale] = {}

    # Ensure default locale has fallback translations
    if DEFAULT_LOCALE not in _TRANSLATIONS:
        _TRANSLATIONS[DEFAULT_LOCALE] = {}

    return _TRANSLATIONS


def get_locale_from_request(request: Any) -> str:
    """Extract locale from FastAPI request headers."""
    # Check Accept-Language header
    accept_language = request.headers.get("accept-language")
    if accept_language:
        # Parse Accept-Language header (e.g., "en-US,en;q=0.9,es;q=0.8")
        for lang_range in accept_language.split(","):
            lang = lang_range.split(";")[0].strip()
            if lang and len(lang) >= 2:
                # Normalize to our format (e.g., "en-US")
                if "-" in lang:
                    parts = lang.split("-")
                    normalized = f"{parts[0].lower()}-{parts[1].upper()}"
                else:
                    normalized = f"{lang.lower()}-{lang.lower().upper()}"

                if normalized in SUPPORTED_LOCALES:
                    return normalized
                # Try just the language part
                lang_only = f"{lang.lower()}-{lang.lower().upper()}"
                if lang_only in SUPPORTED_LOCALES:
                    return lang_only

    return DEFAULT_LOCALE


def clear_translation_cache() -> None:
    """Clear the translation cache to force reload."""
    global _TRANSLATIONS
    _TRANSLATIONS.clear()


def t(key: str, locale: str | None = None, **kwargs: Any) -> str:
    """Translate a key to localized text."""
    if not locale:
        locale = DEFAULT_LOCALE

    # Load translations if not already loaded
    translations = _load_translations()

    # Get translations for locale, fallback to default
    locale_translations: dict[str, Any] = translations.get(locale, {})
    if not locale_translations and locale != DEFAULT_LOCALE:
        locale_translations = translations.get(DEFAULT_LOCALE, {})

    # Handle nested keys with dot notation
    def get_nested_value(data: dict[str, Any], key_path: str) -> str:
        keys = key_path.split('.')
        current: Any = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return key_path  # Return original key if not found
        return str(current) if current is not None else key_path

    # Get translation, fallback to key if not found
    translation = get_nested_value(locale_translations, key)

    # If not found in current locale and not default, try default locale
    if translation == key and locale != DEFAULT_LOCALE:
        default_translations = translations.get(DEFAULT_LOCALE, {})
        translation = get_nested_value(default_translations, key)

    # Simple string formatting
    if kwargs:
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError):
            return translation

    return translation


def tn(key: str, count: int, locale: str | None = None, **kwargs: Any) -> str:
    """Translate with pluralization."""
    # Simple pluralization - in production use proper plural rules
    if count == 1:
        return t(key, locale=locale, **kwargs)
    else:
        plural_key = f"{key}_plural"
        return t(plural_key, locale=locale, count=count, **kwargs)


def format_datetime(dt: datetime | None, locale: str | None = None, timezone: str | None = None) -> str:
    """Format datetime with locale and timezone."""
    if not dt:
        return ""

    if not locale:
        locale = DEFAULT_LOCALE

    # Convert to target timezone if specified
    if timezone:
        try:
            target_tz = ZoneInfo(timezone)
            if dt.tzinfo is None:
                # Assume UTC if no timezone info
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            dt = dt.astimezone(target_tz)
        except Exception:
            # Fallback to original datetime if timezone conversion fails
            pass

    # Format based on locale
    if locale.startswith("es-"):
        return dt.strftime("%d/%m/%Y %H:%M")
    elif locale.startswith("pt-"):
        return dt.strftime("%d/%m/%Y %H:%M")
    else:  # Default to en-US format
        return dt.strftime("%m/%d/%Y %I:%M %p")
