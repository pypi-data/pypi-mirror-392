"""Content safety guards for translations."""

import asyncio
import re
from dataclasses import dataclass
from typing import List, Optional
from anthropic import Anthropic


@dataclass
class SafetyCheckResult:
    """Result of a safety check."""
    is_safe: bool
    flags: List[str]
    reason: str = ""


class SafetyGuard:
    """Content safety guard to prevent harmful translations."""

    # Default sensitive patterns
    DEFAULT_PATTERNS = [
        r'\b(kill|die|death|murder)\b',
        r'\b(hate|stupid|idiot|dumb)\b',
        r'\b(damn|hell|crap)\b',
        r'\b(racist|sexist|discrimination)\b',
    ]

    def __init__(
        self,
        api_key: str,
        custom_blocklist: List[str] = None,
        use_ai_check: bool = True,
        model: str = "claude-3-5-haiku-20241022"
    ):
        self.api_key = api_key
        self.custom_blocklist = custom_blocklist or []
        self.use_ai_check = use_ai_check
        self.model = model
        self.client = Anthropic(api_key=api_key) if use_ai_check else None

        # Compile regex patterns
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.DEFAULT_PATTERNS]

        # Add custom blocklist patterns
        for word in self.custom_blocklist:
            self.patterns.append(re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE))

    async def check_source_text(self, text: str) -> SafetyCheckResult:
        """Check if source text is appropriate for translation."""
        flags = []

        # Quick regex check
        for pattern in self.patterns:
            match = pattern.search(text)
            if match:
                flags.append(f"Contains potentially sensitive pattern: {match.group()}")

        # AI-based deep check
        if self.use_ai_check:
            is_safe, reason = await self._ai_safety_check(text)
            if not is_safe:
                return SafetyCheckResult(is_safe=False, flags=flags, reason=reason)

        # If we have flags but AI says safe, return with warnings
        return SafetyCheckResult(
            is_safe=len(flags) == 0,
            flags=flags,
            reason=""
        )

    async def _ai_safety_check(self, text: str) -> tuple[bool, str]:
        """Use AI to check if text is appropriate."""
        prompt = f"""You are a content safety filter for a translation system.

Analyze this text and determine if it contains:
- Abusive language
- Hate speech
- Profanity (unless it's a legitimate error message)
- Discriminatory content
- Harmful instructions

Text to check: "{text}"

Context: This will be translated and used in a business application UI.

Respond with ONLY:
SAFE - if the text is appropriate for professional translation
UNSAFE: [reason] - if the text should be flagged

Response:"""

        loop = asyncio.get_event_loop()

        def _call_api():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()

        result = await loop.run_in_executor(None, _call_api)

        if result.startswith("SAFE"):
            return True, ""
        else:
            reason = result.replace("UNSAFE:", "").strip()
            return False, reason

    async def check_translation(
        self,
        original: str,
        translated: str,
        language: str
    ) -> SafetyCheckResult:
        """Verify translation is accurate and doesn't introduce harmful content."""
        if not self.use_ai_check:
            return SafetyCheckResult(is_safe=True, flags=[], reason="")

        prompt = f"""Verify this translation is accurate and appropriate:

Original (English): "{original}"
Translation ({language}): "{translated}"

Check:
1. Is the translation accurate?
2. Does it preserve the professional tone?
3. Does it introduce any offensive/harmful content not in the original?

Respond with ONLY:
APPROVED - if translation is good
REJECT: [reason] - if there's an issue

Response:"""

        loop = asyncio.get_event_loop()

        def _call_api():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()

        result = await loop.run_in_executor(None, _call_api)

        if result.startswith("APPROVED"):
            return SafetyCheckResult(is_safe=True, flags=[], reason="")
        else:
            reason = result.replace("REJECT:", "").strip()
            return SafetyCheckResult(is_safe=False, flags=["Translation rejected"], reason=reason)
