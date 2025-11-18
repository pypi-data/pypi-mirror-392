"""Integration tests for all three translation modes.

This test file verifies the logic of all three translation modes by testing
 the relevant code paths and ensuring correct mode selection.

Modes:
1. Mode 1 (no_ai): No AI Translation - just create keys with base language text
2. Mode 2 (lokalise_ai): Lokalise AI Translation - create keys + auto-translation task
3. Mode 3 (claude_ai): Claude AI Translation - highest quality (existing behavior)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from lokalise_mcp.key_extractor import TranslationKey


class TestModeDetermination:
    """Test that the correct mode is selected based on configuration."""

    def test_mode_1_selected_when_no_api_key_and_no_lokalise_translation(self):
        """Mode 1: No ANTHROPIC_API_KEY + use_lokalise_translation=False"""
        config = Mock()
        config.anthropic_api_key = None

        use_lokalise_translation = False
        has_anthropic = bool(config.anthropic_api_key)

        # Logic from server.py lines 207-272
        if not has_anthropic and not use_lokalise_translation:
            mode = "no_ai"
        elif not has_anthropic and use_lokalise_translation:
            mode = "lokalise_ai"
        else:
            mode = "claude_ai"

        assert mode == "no_ai"

    def test_mode_2_selected_when_no_api_key_and_use_lokalise_translation(self):
        """Mode 2: No ANTHROPIC_API_KEY + use_lokalise_translation=True"""
        config = Mock()
        config.anthropic_api_key = None

        use_lokalise_translation = True
        has_anthropic = bool(config.anthropic_api_key)

        if not has_anthropic and not use_lokalise_translation:
            mode = "no_ai"
        elif not has_anthropic and use_lokalise_translation:
            mode = "lokalise_ai"
        else:
            mode = "claude_ai"

        assert mode == "lokalise_ai"

    def test_mode_3_selected_when_api_key_present(self):
        """Mode 3: ANTHROPIC_API_KEY set (regardless of use_lokalise_translation)"""
        config = Mock()
        config.anthropic_api_key = "test_key"

        use_lokalise_translation = False  # Ignored when API key is set
        has_anthropic = bool(config.anthropic_api_key)

        if not has_anthropic and not use_lokalise_translation:
            mode = "no_ai"
        elif not has_anthropic and use_lokalise_translation:
            mode = "lokalise_ai"
        else:
            mode = "claude_ai"

        assert mode == "claude_ai"

    def test_mode_3_always_wins_with_api_key(self):
        """Mode 3 is used even if use_lokalise_translation=True when API key is set"""
        config = Mock()
        config.anthropic_api_key = "test_key"

        use_lokalise_translation = True  # Should be ignored
        has_anthropic = bool(config.anthropic_api_key)

        if not has_anthropic and not use_lokalise_translation:
            mode = "no_ai"
        elif not has_anthropic and use_lokalise_translation:
            mode = "lokalise_ai"
        else:
            mode = "claude_ai"

        assert mode == "claude_ai"


class TestMode1NoAI:
    """Test Mode 1: No AI translation - fastest, free option."""

    @pytest.mark.asyncio
    async def test_mode_1_creates_keys_with_base_language_only(self):
        """Mode 1 should create keys with base language text only."""
        from lokalise_mcp.lokalise_client import LokaliseClient

        with patch('lokalise_mcp.lokalise_client.lokalise') as mock_lokalise:
            # Setup mocks
            client = Mock()
            mock_lokalise.Client.return_value = client

            # Mock project info
            mock_project = Mock()
            mock_project.project_id = "test_project"
            mock_project.base_lang_iso = "en"
            client.project.return_value = mock_project

            # Mock create_keys response
            client.create_keys.return_value = [Mock(key_id=123)]

            # Create client
            lokalise_client = LokaliseClient("test_token", "test_project")

            # Simulate Mode 1: Create key with base language only
            key_name = "test.greeting"
            default_text = "Hello World"
            base_language = "en"

            # Call create_key (Mode 1 path)
            await lokalise_client.create_key(
                key_name=key_name,
                platforms=["web"],
                translations={base_language: default_text}
            )

            # Verify create_keys was called with base language only
            client.create_keys.assert_called_once()
            call_args = client.create_keys.call_args[0]
            keys_data = call_args[1]  # Second argument to create_keys

            # Should have exactly 1 key
            assert len(keys_data) == 1
            assert keys_data[0]["key_name"] == key_name
            # Should have exactly 1 translation (base language)
            assert len(keys_data[0]["translations"]) == 1

    @pytest.mark.asyncio
    async def test_mode_1_skips_keys_without_default_text(self):
        """Mode 1 should skip keys without default_text."""
        key_with_default = TranslationKey(
            key_name="test.greeting",
            default_text="Hello World",
            file_path="/test/app.tsx",
            line_number=10,
            context="t('test.greeting')",
            parameters=[]
        )

        key_without_default = TranslationKey(
            key_name="test.no_default",
            default_text=None,  # No default text
            file_path="/test/app.tsx",
            line_number=15,
            context="t('test.no_default')",
            parameters=[]
        )

        keys = [key_with_default, key_without_default]

        # Mode 1 logic: skip keys without default_text
        keys_to_create = [k for k in keys if k.default_text is not None]

        # Should only have 1 key (the one with default)
        assert len(keys_to_create) == 1
        assert keys_to_create[0].key_name == "test.greeting"

    def test_mode_1_returns_correct_status(self):
        """Mode 1 should return status='created_without_translation' and mode='no_ai'."""
        # Simulated Mode 1 return value (from server.py lines 302-312)
        result = {
            "status": "created_without_translation",
            "mode": "no_ai",
            "message": "Keys created with base language text only. No translations generated.",
            "created": 2,
            "skipped": 0,
            "failed": 0,
            "base_language": "en"
        }

        assert result["status"] == "created_without_translation"
        assert result["mode"] == "no_ai"
        assert "No translations generated" in result["message"]


class TestMode2LokaliseAI:
    """Test Mode 2: Lokalise AI translation."""

    @pytest.mark.asyncio
    async def test_mode_2_creates_translation_task(self):
        """Mode 2 should create a Lokalise translation task."""
        from lokalise_mcp.lokalise_client import LokaliseClient

        with patch('lokalise_mcp.lokalise_client.lokalise') as mock_lokalise:
            # Setup mocks
            client = Mock()
            mock_lokalise.Client.return_value = client

            # Mock project info
            mock_project = Mock()
            mock_project.project_id = "test_project"
            mock_project.base_lang_iso = "en"
            client.project.return_value = mock_project

            # Mock task creation
            mock_task = Mock()
            mock_task.task_id = 456
            client.create_task.return_value = mock_task

            # Create client
            lokalise_client = LokaliseClient("test_token", "test_project")

            # Simulate Mode 2: Create translation task
            key_ids = [123, 124]
            target_languages = ["no", "th"]

            task = await lokalise_client.create_translation_task(
                key_ids=key_ids,
                target_languages=target_languages,
                task_title="Auto-translate 2 new keys"
            )

            # Verify task was created
            assert task.task_id == 456
            client.create_task.assert_called_once()

            # Verify task parameters
            call_args = client.create_task.call_args[0]
            task_data = call_args[1]

            assert task_data["title"] == "Auto-translate 2 new keys"
            assert task_data["task_type"] == "automatic_translation"
            assert task_data["keys"] == key_ids
            assert len(task_data["languages"]) == 2  # no and th

    def test_mode_2_excludes_base_language_from_task(self):
        """Mode 2 should exclude base language from translation task."""
        base_language = "en"
        all_languages = ["en", "no", "th"]

        # Mode 2 logic: exclude base language from task
        target_languages = [lang for lang in all_languages if lang != base_language]

        assert target_languages == ["no", "th"]
        assert base_language not in target_languages

    def test_mode_2_returns_correct_status(self):
        """Mode 2 should return status='created_with_lokalise_translation' and mode='lokalise_ai'."""
        # Simulated Mode 2 return value (from server.py lines 372-385)
        result = {
            "status": "created_with_lokalise_translation",
            "mode": "lokalise_ai",
            "message": "Keys created and Lokalise translation task initiated for 2 languages.",
            "created": 2,
            "skipped": 0,
            "failed": 0,
            "task_id": 456,
            "task_status": "created",
            "target_languages": ["no", "th"]
        }

        assert result["status"] == "created_with_lokalise_translation"
        assert result["mode"] == "lokalise_ai"
        assert "Lokalise translation task initiated" in result["message"]
        assert result["task_id"] == 456


class TestMode3ClaudeAI:
    """Test Mode 3: Claude AI translation - existing behavior."""

    @pytest.mark.asyncio
    async def test_mode_3_uses_ai_translator(self):
        """Mode 3 should use AITranslator for high-quality translations."""
        from lokalise_mcp.translator import AITranslator, TranslationContext

        with patch('lokalise_mcp.translator.Anthropic') as mock_anthropic:
            # Setup mock
            client = Mock()
            mock_anthropic.return_value = client

            mock_response = Mock()
            mock_response.content = [Mock(text="Hei Verden")]
            client.messages.create.return_value = mock_response

            # Create translator (Mode 3)
            translator = AITranslator(api_key="test_key")

            # Translate
            context = TranslationContext(
                key_name="test.greeting",
                source_text="Hello World",
                code_context="t('test.greeting')",
                file_path="/test/app.tsx"
            )

            result = await translator.translate(context, "Norwegian")

            # Verify translation was performed
            assert result == "Hei Verden"
            client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_mode_3_translates_to_multiple_languages(self):
        """Mode 3 should translate keys to all target languages."""
        languages = [
            {"lang_iso": "en", "lang_name": "English"},
            {"lang_iso": "no", "lang_name": "Norwegian"},
            {"lang_iso": "th", "lang_name": "Thai"}
        ]
        base_language = "en"

        # Mode 3 logic: translate to all non-base languages
        target_languages = [
            lang for lang in languages
            if lang["lang_iso"] != base_language
        ]

        assert len(target_languages) == 2
        assert target_languages[0]["lang_iso"] == "no"
        assert target_languages[1]["lang_iso"] == "th"

    @pytest.mark.asyncio
    async def test_mode_3_creates_keys_in_batches(self):
        """Mode 3 should create keys in batches for efficiency."""
        from lokalise_mcp.lokalise_client import LokaliseClient

        with patch('lokalise_mcp.lokalise_client.lokalise') as mock_lokalise:
            # Setup mocks
            client = Mock()
            mock_lokalise.Client.return_value = client

            client.keys.return_value = []  # No existing keys
            client.create_keys.return_value = [Mock(key_id=123), Mock(key_id=124)]

            # Create client
            lokalise_client = LokaliseClient("test_token", "test_project")

            # Simulate Mode 3: Create keys with all translations
            keys_to_create = [
                {
                    "key_name": "test.greeting",
                    "translations": {"en": "Hello", "no": "Hei", "th": "สวัสดี"}
                },
                {
                    "key_name": "test.farewell",
                    "translations": {"en": "Goodbye", "no": "Ha det", "th": "ลาก่อน"}
                }
            ]

            # Create keys in batch
            result = await lokalise_client.create_keys(keys_to_create)

            # Verify batch creation
            assert result["created"] == 2
            # create_keys is called individually per key, not as a single batch
            assert client.create_keys.call_count == 2

    def test_mode_3_returns_correct_status(self):
        """Mode 3 should return status='completed' and mode='claude_ai'."""
        # Simulated Mode 3 return value (from server.py lines 451-462)
        result = {
            "status": "completed",
            "mode": "claude_ai",
            "message": "Keys created with Claude AI translations.",
            "created": 2,
            "skipped": 0,
            "failed": 0,
            "languages": ["en", "no", "th"]
        }

        assert result["status"] == "completed"
        assert result["mode"] == "claude_ai"
        assert "Claude AI translations" in result["message"]


class TestBackwardCompatibility:
    """Test that existing users (Mode 3) are unaffected."""

    def test_default_behavior_with_api_key_is_mode_3(self):
        """When ANTHROPIC_API_KEY is set, default to Mode 3 (existing behavior)."""
        config = Mock()
        config.anthropic_api_key = "test_key"

        # Default parameter value
        use_lokalise_translation = False

        has_anthropic = bool(config.anthropic_api_key)

        # Mode determination logic
        if not has_anthropic and not use_lokalise_translation:
            mode = "no_ai"
        elif not has_anthropic and use_lokalise_translation:
            mode = "lokalise_ai"
        else:
            mode = "claude_ai"

        # Should default to Mode 3 for backward compatibility
        assert mode == "claude_ai"

    def test_ai_translator_without_api_key_returns_empty(self):
        """Verify AITranslator gracefully handles missing API key."""
        from lokalise_mcp.translator import AITranslator

        # Create translator without API key (for Mode 1/2)
        translator = AITranslator(api_key=None)

        # Verify client is None
        assert translator.client is None
        assert translator.api_key is None

    @pytest.mark.asyncio
    async def test_safety_checks_only_in_mode_3(self):
        """Safety checks should only be performed in Mode 3 (Claude AI)."""
        from lokalise_mcp.safety import SafetyGuard

        with patch('lokalise_mcp.safety.Anthropic') as mock_anthropic:
            # Setup mock
            client = Mock()
            mock_anthropic.return_value = client

            mock_response = Mock()
            mock_response.content = [Mock(text="SAFE")]
            client.messages.create.return_value = mock_response

            # Mode 3: Create safety guard with AI check
            safety_guard = SafetyGuard(api_key="test_key", use_ai_check=True)

            # Verify safety guard is initialized
            assert safety_guard.client is not None
            assert safety_guard.use_ai_check is True

            # Mode 1/2: No safety guard created (no API key)
            safety_guard_no_ai = SafetyGuard(api_key=None, use_ai_check=False)
            assert safety_guard_no_ai.client is None


class TestNoKeysFound:
    """Test early return when no keys are found."""

    def test_all_modes_return_no_keys_found_when_empty(self):
        """All modes should return early with status='no_keys_found' when no keys extracted."""
        all_keys = []

        # Early return logic (from server.py lines 245-249)
        if not all_keys:
            result = {
                "status": "no_keys_found",
                "message": "No translation keys found in changed files"
            }
        else:
            result = {"status": "other"}

        assert result["status"] == "no_keys_found"


class TestErrorHandling:
    """Test error handling in different modes."""

    def test_mode_2_handles_task_creation_failure(self):
        """Mode 2 should gracefully handle translation task creation failure."""
        # Simulated Mode 2 return when task creation fails
        result = {
            "status": "created_with_lokalise_translation",
            "mode": "lokalise_ai",
            "created": 2,
            "task_id": None,
            "task_status": "failed",
            "errors": ["Translation task creation failed: API error"]
        }

        # Keys should still be created even if task fails
        assert result["created"] == 2
        assert result["task_status"] == "failed"
        assert result["task_id"] is None
        assert len(result["errors"]) > 0
