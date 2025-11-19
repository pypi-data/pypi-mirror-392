"""
Connection Score Calculator for TIER 2 Analytics.

Calculates weighted connection score (0-100) based on multiple metrics.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ConnectionScoreCalculator:
    """Calculate connection score from thread metrics."""

    # Weights for Connection Score formula
    WEIGHTS = {
        "ai_interest": 0.30,  # 30% - AI interest score
        "response_trend": 0.25,  # 25% - Response trend
        "message_balance": 0.20,  # 20% - Message balance
        "conversation_depth": 0.15,  # 15% - Conversation depth
        "contact_responsiveness": 0.10,  # 10% - Contact responsiveness
    }

    @classmethod
    def calculate(cls, metrics: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate connection score from thread metrics.

        Args:
            metrics: Dictionary containing all TIER 1 and TIER 2 metrics

        Returns:
            {
                "connection_score": 0-100,
                "connection_level": "excellent|good|fair|poor",
                "breakdown": {
                    "ai_interest": 0-100,
                    "response_trend": 0-100,
                    "message_balance": 0-100,
                    "conversation_depth": 0-100,
                    "contact_responsiveness": 0-100
                }
            }
        """
        try:
            # Normalize each metric to 0-100 scale (convert to float)
            normalized = {
                "ai_interest": float(cls._normalize_ai_interest(metrics)),
                "response_trend": float(cls._normalize_response_trend(metrics)),
                "message_balance": float(cls._normalize_message_balance(metrics)),
                "conversation_depth": float(cls._normalize_conversation_depth(metrics)),
                "contact_responsiveness": float(cls._normalize_contact_responsiveness(metrics)),
            }

            # Calculate weighted score
            connection_score = sum(
                normalized[key] * cls.WEIGHTS[key]
                for key in cls.WEIGHTS.keys()
            )

            # Determine connection level
            if connection_score >= 70:
                connection_level = "excellent"
            elif connection_score >= 50:
                connection_level = "good"
            elif connection_score >= 30:
                connection_level = "fair"
            else:
                connection_level = "poor"

            return {
                "connection_score": round(connection_score, 1),
                "connection_level": connection_level,
                "breakdown": {k: round(v, 1) for k, v in normalized.items()}
            }

        except Exception as e:
            logger.error(f"Connection score calculation failed: {e}")
            return {
                "connection_score": 50.0,
                "connection_level": "fair",
                "breakdown": {
                    "ai_interest": 50.0,
                    "response_trend": 50.0,
                    "message_balance": 50.0,
                    "conversation_depth": 50.0,
                    "contact_responsiveness": 50.0
                }
            }

    @staticmethod
    def _normalize_ai_interest(metrics: dict[str, Any]) -> float:
        """Normalize AI interest score (already 0-100)."""
        ai_analysis = metrics.get("ai_analysis", {})
        interest = ai_analysis.get("interest", {})
        return float(interest.get("interest_score", 50))

    @staticmethod
    def _normalize_response_trend(metrics: dict[str, Any]) -> float:
        """
        Normalize response trend to 0-100.

        - Improving (negative %): Higher score
        - Declining (positive %): Lower score
        """
        response_trend = metrics.get("response_trend", {})
        trend_percent = float(response_trend.get("trend_percent", 0))
        trend_direction = response_trend.get("trend_direction", "stable")

        if trend_direction == "improving":
            # -20% to -100% -> 70 to 100
            return min(100, 70 + abs(trend_percent) * 0.3)
        elif trend_direction == "declining":
            # +20% to +100% -> 30 to 0
            return max(0, 30 - trend_percent * 0.3)
        else:  # stable
            return 50.0

    @staticmethod
    def _normalize_message_balance(metrics: dict[str, Any]) -> float:
        """
        Normalize message balance score (already 0-100).

        Balance score = 100 - |50 - user_percentage|
        """
        message_balance = metrics.get("message_balance", {})
        return float(message_balance.get("balance_score", 50))

    @staticmethod
    def _normalize_conversation_depth(metrics: dict[str, Any]) -> float:
        """
        Normalize conversation depth to 0-100.

        Based on messages_per_day:
        - 0-5: 0-30
        - 5-10: 30-60
        - 10-20: 60-90
        - >20: 90-100
        """
        conversation_depth = metrics.get("conversation_depth", {})
        msgs_per_day = float(conversation_depth.get("messages_per_day", 0))

        if msgs_per_day <= 5:
            return (msgs_per_day / 5) * 30
        elif msgs_per_day <= 10:
            return 30 + ((msgs_per_day - 5) / 5) * 30
        elif msgs_per_day <= 20:
            return 60 + ((msgs_per_day - 10) / 10) * 30
        else:
            return min(100, 90 + ((msgs_per_day - 20) / 10) * 10)

    @staticmethod
    def _normalize_contact_responsiveness(metrics: dict[str, Any]) -> float:
        """
        Normalize contact responsiveness to 0-100.

        Responsiveness rate is already a percentage (0-100).
        """
        contact_responsiveness = metrics.get("contact_responsiveness", {})
        return float(contact_responsiveness.get("responsiveness_rate", 50))


def calculate_connection_score(metrics: dict[str, Any]) -> dict[str, Any]:
    """
    Convenience function to calculate connection score.

    Args:
        metrics: Dictionary containing all TIER 1 and TIER 2 metrics

    Returns:
        Connection score result with breakdown
    """
    return ConnectionScoreCalculator.calculate(metrics)
