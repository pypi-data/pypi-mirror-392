"""AI-powered translation service using Claude."""

import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional
from anthropic import Anthropic


@dataclass
class TranslationContext:
    """Context for translating a key."""
    key_name: str
    source_text: str
    code_context: str = ""
    file_path: str = ""
    parameters: List[str] = None
    similar_translations: Dict[str, str] = None


class AITranslator:
    """AI-powered translator using Claude."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-haiku-20241022"):
        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=api_key) if api_key else None

    def _build_translation_prompt(
        self,
        context: TranslationContext,
        target_language: str
    ) -> str:
        """Build a detailed prompt for translation."""
        prompt_parts = [
            f"Translate this UI text to {target_language}:",
            "",
            f"Key: {context.key_name}",
            f"English: \"{context.source_text}\"",
        ]

        if context.parameters:
            prompt_parts.append(f"Parameters: {', '.join(context.parameters)}")
        else:
            prompt_parts.append("Parameters: none")

        if context.code_context:
            prompt_parts.extend([
                "",
                "Context from code:",
                context.code_context
            ])

        if context.similar_translations:
            prompt_parts.extend([
                "",
                "Similar translations in this project:",
            ])
            for key, value in context.similar_translations.items():
                prompt_parts.append(f"- {key}: \"{value}\"")

        prompt_parts.extend([
            "",
            "Provide a natural, concise translation that:",
            "1. Matches the formality of similar UI elements",
            "2. Is clear and actionable",
            "3. Preserves any parameter placeholders like %{count}",
            "4. Fits the UI context (button/link/heading/etc)",
            "",
            "Respond with ONLY the translated text, no explanations.",
            "",
            "Translation:"
        ])

        return "\n".join(prompt_parts)

    async def translate(
        self,
        context: TranslationContext,
        target_language: str
    ) -> str:
        """Translate a single text to target language."""
        if not self.client:
            return ""

        prompt = self._build_translation_prompt(context, target_language)

        # Run in thread pool since Anthropic SDK is synchronous
        loop = asyncio.get_event_loop()

        def _call_api():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()

        translation = await loop.run_in_executor(None, _call_api)

        # Clean up any quotes that might be added
        translation = translation.strip('"\'')

        return translation

    async def translate_batch(
        self,
        contexts: List[TranslationContext],
        target_language: str
    ) -> List[str]:
        """Translate multiple texts to same language (more efficient)."""
        if not self.client:
            return []

        # Build batch prompt
        prompt_parts = [
            f"Translate these UI texts to {target_language}.",
            "Respond with one translation per line, in order.",
            "Use ONLY the translated text, no numbering or explanations.",
            ""
        ]

        for i, ctx in enumerate(contexts, 1):
            prompt_parts.extend([
                f"{i}. Key: {ctx.key_name}",
                f"   English: \"{ctx.source_text}\"",
                ""
            ])

        prompt_parts.append("Translations (one per line):")
        prompt = "\n".join(prompt_parts)

        loop = asyncio.get_event_loop()

        def _call_api():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()

        result = await loop.run_in_executor(None, _call_api)

        # Parse line-by-line
        translations = [line.strip().strip('"\'') for line in result.split('\n') if line.strip()]

        # Ensure we have the right number
        if len(translations) != len(contexts):
            # Fallback to individual translation
            return [await self.translate(ctx, target_language) for ctx in contexts]

        return translations

    async def translate_to_languages(
        self,
        context: TranslationContext,
        languages: List[str]
    ) -> Dict[str, str]:
        """Translate a single text to multiple languages."""
        if not self.client:
            return {}

        tasks = [
            self.translate(context, lang)
            for lang in languages
        ]

        results = await asyncio.gather(*tasks)

        return {
            lang: translation
            for lang, translation in zip(languages, results)
        }
