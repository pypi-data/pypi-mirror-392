"""
Conversation Analyzer for TIER 2 Analytics.

Provides AI-powered analysis of conversations including:
- Interest score (0-100)
- Sentiment analysis
- Conversation stage detection
- NLP question rate
- Personalized recommendations
"""

import json
import logging
from typing import Any
from uuid import UUID

from flerity_core.domain.ai.bedrock_client import BedrockClient
from flerity_core.domain.ai.cache import AICache

logger = logging.getLogger(__name__)


class ConversationAnalyzer:
    """AI-powered conversation analysis for dating context."""

    def __init__(
        self,
        bedrock_client: BedrockClient,
        cache: AICache | None = None
    ):
        self.bedrock = bedrock_client
        self.cache = cache

    async def analyze_interest(
        self,
        messages: list[dict[str, Any]],
        thread_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Analyze contact's interest level using AI.

        Args:
            messages: List of recent messages (last 20)
            thread_id: Optional thread ID for caching

        Returns:
            {
                "interest_score": 0-100,
                "interest_level": "very_high|high|medium|low",
                "reasoning": "brief explanation",
                "confidence": 0-100
            }
        """
        # Check cache
        if self.cache and thread_id:
            cached = await self.cache.get(f"interest:{thread_id}")
            if cached:
                return cached

        # Build transcript
        transcript = self._build_transcript(messages[-20:])

        prompt = f"""Analise o nível de interesse do contato nesta conversa de namoro e retorne JSON:

{{
  "interest_score": 0-100,
  "interest_level": "very_high|high|medium|low",
  "reasoning": "explicação breve em português",
  "confidence": 0-100
}}

Critérios para avaliar interesse:
- Profundidade das respostas (curtas vs elaboradas)
- Uso de perguntas abertas e curiosidade
- Reciprocidade (compartilha informações pessoais)
- Uso de emojis e humor
- Iniciativa em manter conversa
- Tempo de resposta (se mensagens recentes)

Níveis:
- very_high (80-100): Muito interessado, respostas rápidas e elaboradas
- high (60-79): Interessado, engajado na conversa
- medium (40-59): Interesse moderado, respostas básicas
- low (0-39): Baixo interesse, respostas curtas ou demoradas

Conversa (últimas 20 mensagens):
{transcript}

Responda APENAS com o JSON, sem texto adicional."""

        try:
            response = await self.bedrock.generate_text(
                prompt,
                model_id="amazon.nova-micro-v1:0",  # Use Micro for cost efficiency
                max_tokens=300,
                timeout=10.0
            )

            result = self._parse_json_response(response, {
                "interest_score": 50,
                "interest_level": "medium",
                "reasoning": "Análise não disponível",
                "confidence": 0
            })

            # Normalize interest_level
            score = result.get("interest_score", 50)
            if score >= 80:
                result["interest_level"] = "very_high"
            elif score >= 60:
                result["interest_level"] = "high"
            elif score >= 40:
                result["interest_level"] = "medium"
            else:
                result["interest_level"] = "low"

            # Cache for 6 hours
            if self.cache and thread_id:
                await self.cache.set(f"interest:{thread_id}", result, ttl=21600)

            return result

        except Exception as e:
            logger.error(f"Interest analysis failed: {e}")
            return {
                "interest_score": 50,
                "interest_level": "medium",
                "reasoning": "Análise temporariamente indisponível",
                "confidence": 0
            }

    async def analyze_sentiment(
        self,
        messages: list[dict[str, Any]],
        thread_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Analyze sentiment of conversation.

        Returns:
            {
                "overall_sentiment": "positive|neutral|negative",
                "user_sentiment": "positive|neutral|negative",
                "contact_sentiment": "positive|neutral|negative",
                "sentiment_trend": "improving|stable|declining",
                "confidence": 0-100
            }
        """
        if self.cache and thread_id:
            cached = await self.cache.get(f"sentiment:{thread_id}")
            if cached:
                return cached

        transcript = self._build_transcript(messages[-20:])

        prompt = f"""Analise o sentimento geral desta conversa de namoro e retorne JSON:

{{
  "overall_sentiment": "positive|neutral|negative",
  "user_sentiment": "positive|neutral|negative",
  "contact_sentiment": "positive|neutral|negative",
  "sentiment_trend": "improving|stable|declining",
  "confidence": 0-100
}}

Critérios:
- positive: Tom alegre, emojis positivos, entusiasmo
- neutral: Tom neutro, informativo
- negative: Tom frio, desinteressado, irritado

Trend:
- improving: Sentimento melhorando ao longo da conversa
- stable: Sentimento consistente
- declining: Sentimento piorando

Conversa:
{transcript}

Responda APENAS com o JSON."""

        try:
            response = await self.bedrock.generate_text(
                prompt,
                model_id="amazon.nova-micro-v1:0",
                max_tokens=200,
                timeout=10.0
            )

            result = self._parse_json_response(response, {
                "overall_sentiment": "neutral",
                "user_sentiment": "neutral",
                "contact_sentiment": "neutral",
                "sentiment_trend": "stable",
                "confidence": 0
            })

            if self.cache and thread_id:
                await self.cache.set(f"sentiment:{thread_id}", result, ttl=21600)

            return result

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "overall_sentiment": "neutral",
                "user_sentiment": "neutral",
                "contact_sentiment": "neutral",
                "sentiment_trend": "stable",
                "confidence": 0
            }

    async def detect_conversation_stage(
        self,
        messages: list[dict[str, Any]],
        thread_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Detect current conversation stage.

        Returns:
            {
                "stage": "getting_to_know|building_rapport|flirting|planning_date|cooling_off|ghosting",
                "confidence": 0-100,
                "next_steps": ["sugestão 1", "sugestão 2"]
            }
        """
        if self.cache and thread_id:
            cached = await self.cache.get(f"stage:{thread_id}")
            if cached:
                return cached

        transcript = self._build_transcript(messages[-20:])

        prompt = f"""Identifique a fase atual desta conversa de namoro e retorne JSON:

{{
  "stage": "getting_to_know|building_rapport|flirting|planning_date|cooling_off|ghosting",
  "confidence": 0-100,
  "next_steps": ["sugestão 1", "sugestão 2"]
}}

Fases:
- getting_to_know: Perguntas básicas, conhecendo interesses
- building_rapport: Compartilhando histórias, criando conexão
- flirting: Tom mais íntimo, brincadeiras, emojis românticos
- planning_date: Discutindo encontro, trocando contatos
- cooling_off: Respostas mais lentas/curtas, interesse diminuindo
- ghosting: Sem resposta há muito tempo

Next steps: 2 sugestões específicas e acionáveis em português.

Conversa:
{transcript}

Responda APENAS com o JSON."""

        try:
            response = await self.bedrock.generate_text(
                prompt,
                model_id="amazon.nova-micro-v1:0",
                max_tokens=300,
                timeout=10.0
            )

            result = self._parse_json_response(response, {
                "stage": "getting_to_know",
                "confidence": 0,
                "next_steps": ["Continue a conversa naturalmente"]
            })

            if self.cache and thread_id:
                await self.cache.set(f"stage:{thread_id}", result, ttl=21600)

            return result

        except Exception as e:
            logger.error(f"Stage detection failed: {e}")
            return {
                "stage": "getting_to_know",
                "confidence": 0,
                "next_steps": ["Continue a conversa naturalmente"]
            }

    async def analyze_question_rate(
        self,
        messages: list[dict[str, Any]],
        thread_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Analyze question rate using NLP (not regex).

        Returns:
            {
                "user_question_rate": 0-100,
                "contact_question_rate": 0-100,
                "user_questions": int,
                "contact_questions": int,
                "engagement_level": "high|medium|low"
            }
        """
        if self.cache and thread_id:
            cached = await self.cache.get(f"questions:{thread_id}")
            if cached:
                return cached

        # Separate user and contact messages
        user_msgs = [m for m in messages if m.get("sender") == "user"]
        contact_msgs = [m for m in messages if m.get("sender") == "contact"]

        # Analyze user questions
        user_result = await self._analyze_questions_batch(user_msgs, "user")
        contact_result = await self._analyze_questions_batch(contact_msgs, "contact")

        result = {
            "user_question_rate": user_result["question_rate"],
            "contact_question_rate": contact_result["question_rate"],
            "user_questions": user_result["question_count"],
            "contact_questions": contact_result["question_count"],
            "engagement_level": self._calculate_engagement_level(
                user_result["question_rate"],
                contact_result["question_rate"]
            )
        }

        if self.cache and thread_id:
            await self.cache.set(f"questions:{thread_id}", result, ttl=21600)

        return result

    async def _analyze_questions_batch(
        self,
        messages: list[dict[str, Any]],
        sender: str
    ) -> dict[str, Any]:
        """Analyze questions in a batch of messages using NLP."""
        if not messages:
            return {"question_rate": 0.0, "question_count": 0}

        # Build messages list for analysis
        msgs_text = "\n".join([
            f"{i}: {m.get('text', '')}"
            for i, m in enumerate(messages[-50:])  # Last 50 messages max
        ])

        prompt = f"""Analise estas mensagens e identifique quais são perguntas.
Considere perguntas diretas, indiretas, retóricas e implícitas.

Retorne JSON:
{{
  "questions": [índices das mensagens que são perguntas],
  "question_rate": percentual (0-100)
}}

Mensagens:
{msgs_text}

Responda APENAS com o JSON."""

        try:
            response = await self.bedrock.generate_text(
                prompt,
                model_id="amazon.nova-micro-v1:0",
                max_tokens=200,
                timeout=10.0
            )

            result = self._parse_json_response(response, {
                "questions": [],
                "question_rate": 0.0
            })

            question_count = len(result.get("questions", []))
            question_rate = (question_count / len(messages)) * 100 if messages else 0.0

            return {
                "question_rate": round(question_rate, 1),
                "question_count": question_count
            }

        except Exception as e:
            logger.error(f"Question analysis failed for {sender}: {e}")
            # Fallback to simple regex
            question_count = sum(
                1 for m in messages
                if "?" in m.get("text", "") or any(
                    word in m.get("text", "").lower()
                    for word in ["como", "quando", "onde", "por que", "qual", "quem", "o que"]
                )
            )
            question_rate = (question_count / len(messages)) * 100 if messages else 0.0
            return {
                "question_rate": round(question_rate, 1),
                "question_count": question_count
            }

    def _calculate_engagement_level(
        self,
        user_rate: float,
        contact_rate: float
    ) -> str:
        """Calculate engagement level based on question rates."""
        avg_rate = (user_rate + contact_rate) / 2
        if avg_rate > 40:
            return "high"
        elif avg_rate > 20:
            return "medium"
        else:
            return "low"

    async def generate_recommendations(
        self,
        thread_metrics: dict[str, Any],
        messages: list[dict[str, Any]],
        thread_id: UUID | None = None
    ) -> list[dict[str, Any]]:
        """
        Generate personalized recommendations based on analytics.

        Returns:
            [
                {
                    "type": "action|warning|encouragement",
                    "priority": "high|medium|low",
                    "text": "recomendação específica",
                    "reasoning": "por que essa recomendação"
                }
            ]
        """
        if self.cache and thread_id:
            cached = await self.cache.get(f"recommendations:{thread_id}")
            if cached:
                return cached

        # Build context from metrics
        context = self._build_metrics_context(thread_metrics)
        transcript = self._build_transcript(messages[-10:])  # Last 10 messages

        prompt = f"""Baseado nesta análise de conversa de namoro, gere 2-3 recomendações específicas e acionáveis:

Métricas:
{context}

Últimas mensagens:
{transcript}

Retorne JSON:
{{
  "recommendations": [
    {{
      "type": "action|warning|encouragement",
      "priority": "high|medium|low",
      "text": "recomendação específica e acionável em português",
      "reasoning": "por que essa recomendação"
    }}
  ]
}}

Tipos:
- action: Sugestão de ação específica
- warning: Alerta sobre comportamento problemático
- encouragement: Encorajamento positivo

Responda APENAS com o JSON."""

        try:
            response = await self.bedrock.generate_text(
                prompt,
                model_id="amazon.nova-micro-v1:0",
                max_tokens=500,
                timeout=15.0
            )

            result = self._parse_json_response(response, {
                "recommendations": []
            })

            recommendations = result.get("recommendations", [])[:3]  # Max 3

            if self.cache and thread_id:
                await self.cache.set(f"recommendations:{thread_id}", recommendations, ttl=21600)

            return recommendations

        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return []

    def _build_transcript(self, messages: list[dict[str, Any]]) -> str:
        """Build conversation transcript for AI analysis."""
        lines = []
        for msg in messages:
            sender = msg.get("sender", "user")
            text = msg.get("text_msg") or msg.get("text", "")
            lines.append(f"{sender}: {text}")
        return "\n".join(lines)

    def _build_metrics_context(self, metrics: dict[str, Any]) -> str:
        """Build metrics context for recommendations."""
        lines = []

        if "message_balance" in metrics:
            balance = metrics["message_balance"]
            lines.append(f"- Message Balance: {balance.get('user_percentage', 0):.1f}% user, {balance.get('contact_percentage', 0):.1f}% contact (score: {balance.get('balance_score', 0):.1f})")

        if "response_times" in metrics:
            rt = metrics["response_times"]
            lines.append(f"- Response Time: {rt.get('avg_response_hours', 0):.1f}h average (interest: {rt.get('interest_level', 'unknown')})")

        if "response_trend" in metrics:
            trend = metrics["response_trend"]
            lines.append(f"- Response Trend: {trend.get('trend_interpretation', 'unknown')} ({trend.get('trend_percent', 0):.1f}%)")

        if "conversation_depth" in metrics:
            depth = metrics["conversation_depth"]
            lines.append(f"- Conversation Depth: {depth.get('messages_per_day', 0):.1f} msgs/day (intensity: {depth.get('intensity_level', 'unknown')})")

        if "recency" in metrics:
            recency = metrics["recency"]
            lines.append(f"- Recency: {recency.get('hours_since_last', 0):.1f}h since last message (status: {recency.get('status', 'unknown')})")

        return "\n".join(lines) if lines else "Métricas não disponíveis"

    def _parse_json_response(
        self,
        response: str,
        default: dict[str, Any]
    ) -> dict[str, Any]:
        """Parse JSON response from AI with fallback."""
        try:
            # Try direct JSON parse
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try to find any JSON object
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            logger.warning(f"Failed to parse JSON response: {response[:200]}")
            return default
