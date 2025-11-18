"""Lokalise API client wrapper."""

import asyncio
from typing import List, Dict, Optional
import lokalise


class LokaliseClient:
    """Client for interacting with Lokalise API."""

    def __init__(self, api_token: str, project_id: str):
        self.api_token = api_token
        self.project_id = project_id
        self.client = lokalise.Client(api_token)
        self._existing_keys_cache: Optional[set] = None

    async def get_project_languages(self) -> List[Dict[str, str]]:
        """Fetch all languages configured in the Lokalise project."""
        # Run in thread pool since lokalise SDK is synchronous
        loop = asyncio.get_event_loop()
        languages = await loop.run_in_executor(
            None,
            lambda: self.client.project_languages(self.project_id)
        )

        return [
            {
                "lang_iso": lang.lang_iso,
                "lang_name": lang.lang_name,
                "is_rtl": getattr(lang, "is_rtl", False),
            }
            for lang in languages
        ]

    async def get_project_info(self) -> Dict:
        """Get project information."""
        loop = asyncio.get_event_loop()
        project = await loop.run_in_executor(
            None,
            lambda: self.client.project(self.project_id)
        )

        return {
            "project_id": project.project_id,
            "name": project.name,
            "base_lang_iso": getattr(project, "base_lang_iso", "en"),
        }

    async def _load_existing_keys(self):
        """Load all existing keys into cache."""
        if self._existing_keys_cache is not None:
            return

        loop = asyncio.get_event_loop()
        keys = await loop.run_in_executor(
            None,
            lambda: self.client.keys(self.project_id)
        )

        self._existing_keys_cache = set()
        for key in keys:
            # Keys might be platform-specific or simple strings
            if isinstance(key.key_name, dict):
                # Platform-specific: {"web": "key.name", "ios": "key_name"}
                self._existing_keys_cache.update(key.key_name.values())
            else:
                self._existing_keys_cache.add(key.key_name)

    async def key_exists(self, key_name: str) -> bool:
        """Check if a key already exists in Lokalise."""
        await self._load_existing_keys()
        return key_name in self._existing_keys_cache

    async def create_keys(self, keys: List[Dict]) -> Dict:
        """Create multiple translation keys in Lokalise.

        Args:
            keys: List of dicts with structure:
                {
                    "key_name": "products.title",
                    "translations": {
                        "en": "Products",
                        "no": "Produkter"
                    }
                }

        Returns:
            Dict with created/failed counts
        """
        created = 0
        failed = 0
        skipped = 0
        errors = []

        loop = asyncio.get_event_loop()

        for key_data in keys:
            key_name = key_data["key_name"]
            translations = key_data["translations"]

            # Check if exists
            if await self.key_exists(key_name):
                skipped += 1
                continue

            try:
                # Format for Lokalise API
                lokalise_key = {
                    "key_name": key_name,
                    "platforms": ["web"],
                    "translations": [
                        {
                            "language_iso": lang_iso,
                            "translation": text
                        }
                        for lang_iso, text in translations.items()
                    ]
                }

                # Create key
                await loop.run_in_executor(
                    None,
                    lambda: self.client.create_keys(self.project_id, [lokalise_key])
                )

                created += 1

                # Update cache
                if self._existing_keys_cache is not None:
                    self._existing_keys_cache.add(key_name)

            except Exception as e:
                failed += 1
                errors.append(f"{key_name}: {str(e)}")

        return {
            "created": created,
            "failed": failed,
            "skipped": skipped,
            "errors": errors
        }
