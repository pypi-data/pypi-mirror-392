# Phase 5: Optional AI Translations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make Anthropic API key optional and add Lokalise auto-translation support

**Architecture:** Add three translation modes: (1) No translation (just create keys), (2) Lokalise auto-translation via Tasks API, (3) Claude AI translation (existing). Anthropic API key becomes optional.

**Tech Stack:** Python 3.11, FastMCP, python-lokalise-api, Anthropic SDK (optional)

---

## Task 1: Make Anthropic API Key Optional in Config

**Files:**
- Modify: `src/lokalise_mcp/config.py:33-44`
- Test: `tests/test_config.py` (if exists, else create)

**Step 1: Write failing test for optional Anthropic key**

Create `tests/test_config.py` (if it doesn't exist):
```python
"""Tests for configuration validation."""
import pytest
from lokalise_mcp.config import Config


def test_config_validates_without_anthropic_key():
    """Config should be valid without Anthropic API key."""
    config = Config(
        lokalise_api_token="test-token",
        lokalise_project_id="test-project-id",
        anthropic_api_key=""  # Empty is OK now
    )

    errors = config.validate()

    # Should only complain about missing Lokalise credentials, not Anthropic
    assert "LOKALISE_API_TOKEN" not in [e for e in errors]
    assert "LOKALISE_PROJECT_ID" not in [e for e in errors]
    assert "ANTHROPIC_API_KEY" not in [e for e in errors]


def test_config_still_validates_lokalise_credentials():
    """Config should require Lokalise credentials."""
    config = Config(
        lokalise_api_token="",
        lokalise_project_id="",
        anthropic_api_key=""
    )

    errors = config.validate()

    assert "LOKALISE_API_TOKEN is required" in errors
    assert "LOKALISE_PROJECT_ID is required" in errors
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py::test_config_validates_without_anthropic_key -v`

Expected: FAIL (currently Anthropic key is required)

**Step 3: Update config validation to make Anthropic optional**

In `src/lokalise_mcp/config.py`, modify the `validate` method:
```python
def validate(self) -> list[str]:
    """Validate required configuration. Returns list of errors."""
    errors = []

    if not self.lokalise_api_token:
        errors.append("LOKALISE_API_TOKEN is required")
    if not self.lokalise_project_id:
        errors.append("LOKALISE_PROJECT_ID is required")
    # ANTHROPIC_API_KEY is now optional - only needed for Claude AI translations

    return errors
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`

Expected: PASS (both tests pass)

**Step 5: Commit**

```bash
git add tests/test_config.py src/lokalise_mcp/config.py
git commit -m "feat: make Anthropic API key optional in config"
```

---

## Task 2: Add Lokalise Task Creation Method

**Files:**
- Modify: `src/lokalise_mcp/lokalise_client.py` (add method ~line 140)
- Test: `tests/test_lokalise_client.py`

**Step 1: Write failing test for task creation**

In `tests/test_lokalise_client.py`, add:
```python
import pytest
from unittest.mock import Mock, AsyncMock
from lokalise_mcp.lokalise_client import LokaliseClient


@pytest.mark.asyncio
async def test_create_translation_task():
    """Should create automatic translation task in Lokalise."""
    # Mock the Lokalise client
    mock_client = Mock()
    mock_client.create_task = Mock(return_value={
        'task_id': 12345,
        'task_type': 'automatic_translation',
        'title': 'Auto-translate new keys'
    })

    client = LokaliseClient(
        api_token="test-token",
        project_id="test-project"
    )
    client.client = mock_client

    # Create task for 3 keys in 2 languages
    result = await client.create_translation_task(
        key_ids=[1, 2, 3],
        target_languages=["no", "ne"],
        task_title="Test task"
    )

    # Verify task was created with correct parameters
    assert result['task_id'] == 12345
    assert result['task_type'] == 'automatic_translation'

    # Verify API was called correctly
    call_args = mock_client.create_task.call_args
    assert call_args[0][0] == "test-project"
    task_data = call_args[0][1]
    assert task_data['task_type'] == 'automatic_translation'
    assert task_data['keys'] == [1, 2, 3]
    assert len(task_data['languages']) == 2
    assert task_data['auto_close_task'] is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lokalise_client.py::test_create_translation_task -v`

Expected: FAIL (method doesn't exist yet)

**Step 3: Add create_translation_task method**

In `src/lokalise_mcp/lokalise_client.py`, add this method:
```python
async def create_translation_task(
    self,
    key_ids: List[int],
    target_languages: List[str],
    task_title: str = "Auto-translate new keys"
) -> dict:
    """Create an automatic translation task in Lokalise.

    This triggers Lokalise's built-in AI translation (Google/DeepL/Lokalise AI).

    Args:
        key_ids: List of key IDs to translate
        target_languages: List of language ISOs to translate to
        task_title: Title for the translation task

    Returns:
        Task data from Lokalise API
    """
    # Build language objects (exclude base language)
    languages = []
    for lang in target_languages:
        if lang != self.base_language_iso:
            languages.append({
                "language_iso": lang,
                "users": []  # Empty = assigned to project owner
            })

    task_data = {
        "title": task_title,
        "task_type": "automatic_translation",
        "keys": key_ids,
        "languages": languages,
        "auto_close_task": True,
        "auto_close_items": True,
        "apply_ai_tm100_matches": True,  # Reuse translation memory exact matches
        "save_ai_translation_to_tm": True  # Save translations to memory
    }

    response = self.client.create_task(self.project_id, task_data)
    return response
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lokalise_client.py::test_create_translation_task -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_lokalise_client.py src/lokalise_mcp/lokalise_client.py
git commit -m "feat: add Lokalise automatic translation task creation"
```

---

## Task 3: Update Translator to Handle Missing API Key

**Files:**
- Modify: `src/lokalise_mcp/translator.py:20-30`
- Test: `tests/test_translator.py`

**Step 1: Write failing test for translator without API key**

In `tests/test_translator.py`, add:
```python
import pytest
from lokalise_mcp.translator import AITranslator, TranslationContext


@pytest.mark.asyncio
async def test_translator_without_api_key_returns_empty():
    """Translator without API key should return empty translations."""
    translator = AITranslator(api_key=None)

    context = TranslationContext(
        key_name="test.key",
        default_text="Hello",
        source_language="en"
    )

    result = await translator.translate(
        context=context,
        target_languages=["no", "ne"]
    )

    # Should return empty dict when no API key
    assert result == {}


def test_translator_initialization_without_key():
    """Translator should initialize without API key."""
    translator = AITranslator(api_key=None)

    assert translator.api_key is None
    assert translator.client is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_translator.py::test_translator_without_api_key_returns_empty -v`

Expected: FAIL (currently crashes without API key)

**Step 3: Update AITranslator to handle missing key**

In `src/lokalise_mcp/translator.py`, modify `__init__` and `translate`:
```python
class AITranslator:
    """AI-powered translator using Claude."""

    def __init__(self, api_key: str = None, model: str = DEFAULT_MODEL):
        """Initialize translator.

        Args:
            api_key: Anthropic API key (optional - if None, no AI translation)
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model

        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None

    async def translate(
        self,
        context: TranslationContext,
        target_languages: List[str]
    ) -> Dict[str, str]:
        """Translate text to target languages using Claude.

        Returns:
            Dictionary mapping language codes to translations.
            Empty dict if no API key provided.
        """
        if not self.client:
            # No AI translation available
            return {}

        # ... existing translation code ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_translator.py -v`

Expected: PASS (both tests pass)

**Step 5: Commit**

```bash
git add tests/test_translator.py src/lokalise_mcp/translator.py
git commit -m "feat: make AI translator work without API key"
```

---

## Task 4: Add use_lokalise_translation Parameter to Server

**Files:**
- Modify: `src/lokalise_mcp/server.py:157-190`
- Test: Integration test via MCP

**Step 1: Add parameter to tool signature**

In `src/lokalise_mcp/server.py`, update `extract_and_sync_translations`:
```python
@mcp.tool()
async def extract_and_sync_translations(
    repo_path: Optional[str] = None,
    base_branch: str = "main",
    batch_size: int = 3,
    auto_approve: bool = False,
    skip_safety_check: bool = False,
    use_lokalise_translation: bool = False  # NEW
) -> Dict:
    """Extract translation keys from git diff and sync to Lokalise.

    Translation modes:
    1. If ANTHROPIC_API_KEY provided: Use Claude AI for translations
    2. If use_lokalise_translation=True: Create Lokalise auto-translation task
    3. Otherwise: Just create keys without translations

    Args:
        repo_path: Path to your project's git repository. Defaults to current working directory.
        base_branch: Git branch to compare against (default: main)
        batch_size: Number of keys to create per batch (default: 3)
        auto_approve: Skip approval prompts and create all keys (default: False)
        skip_safety_check: Skip content safety checks (default: false)
        use_lokalise_translation: Use Lokalise auto-translation instead of Claude (default: False)

    Returns:
        Summary with created/skipped/failed counts
    """
```

**Step 2: Update docstring and add to README**

Update README.md to document the new parameter in the "Available MCP Tools" section.

**Step 3: Commit**

```bash
git add src/lokalise_mcp/server.py README.md
git commit -m "feat: add use_lokalise_translation parameter"
```

---

## Task 5: Implement Mode 1 - No Translation

**Files:**
- Modify: `src/lokalise_mcp/server.py:200-250`

**Step 1: Add logic for no-translation mode**

In `src/lokalise_mcp/server.py`, in the `extract_and_sync_translations` function:
```python
# After extracting keys...

# Determine translation mode
has_anthropic = bool(config.anthropic_api_key)

if not has_anthropic and not use_lokalise_translation:
    # Mode 1: No translation - just create keys
    created_count = 0
    skipped_count = 0
    failed_count = 0

    for key in all_keys:
        try:
            # Check if key exists
            existing = await lokalise_client.get_key_by_name(key.key_name)
            if existing:
                skipped_count += 1
                continue

            # Create key with only base language translation
            await lokalise_client.create_key(
                key_name=key.key_name,
                platforms=["web"],
                translations={
                    base_language: key.default_text or key.key_name
                }
            )
            created_count += 1

        except Exception as e:
            failed_count += 1
            # Log error

    return {
        "status": "created_without_translation",
        "created": created_count,
        "skipped": skipped_count,
        "failed": failed_count,
        "message": f"Created {created_count} keys. Translate manually in Lokalise UI.",
        "next_steps": [
            "1. Go to Lokalise project",
            "2. Select keys to translate",
            "3. Use Lokalise's translation tools (UI or automations)"
        ]
    }
```

**Step 2: Test manually**

Create a test file with a translation key, run the MCP tool without Anthropic key:
```bash
# Remove Anthropic key from env
unset ANTHROPIC_API_KEY

# Run MCP tool (via Claude Code)
"Extract translations without AI"
```

Expected: Keys created with only English text

**Step 3: Commit**

```bash
git add src/lokalise_mcp/server.py
git commit -m "feat: implement no-translation mode (Mode 1)"
```

---

## Task 6: Implement Mode 2 - Lokalise Auto-Translation

**Files:**
- Modify: `src/lokalise_mcp/server.py:250-300`

**Step 1: Add logic for Lokalise translation mode**

In `src/lokalise_mcp/server.py`, add after Mode 1:
```python
elif use_lokalise_translation:
    # Mode 2: Lokalise auto-translation
    created_keys = []
    skipped_count = 0
    failed_count = 0

    # First, create all keys
    for key in all_keys:
        try:
            # Check if key exists
            existing = await lokalise_client.get_key_by_name(key.key_name)
            if existing:
                skipped_count += 1
                continue

            # Create key with only base language
            response = await lokalise_client.create_key(
                key_name=key.key_name,
                platforms=["web"],
                translations={
                    base_language: key.default_text or key.key_name
                }
            )
            created_keys.append({
                "key_id": response['key_id'],
                "key_name": key.key_name
            })

        except Exception as e:
            failed_count += 1

    # Create translation task if we have keys
    task_info = None
    if created_keys:
        key_ids = [k['key_id'] for k in created_keys]

        task_info = await lokalise_client.create_translation_task(
            key_ids=key_ids,
            target_languages=target_languages,
            task_title=f"Auto-translate {len(key_ids)} new keys"
        )

    return {
        "status": "created_with_lokalise_translation",
        "created": len(created_keys),
        "skipped": skipped_count,
        "failed": failed_count,
        "task_id": task_info['task_id'] if task_info else None,
        "message": f"Created {len(created_keys)} keys and Lokalise translation task",
        "next_steps": [
            "1. Lokalise is now translating your keys automatically",
            "2. Check task progress in Lokalise UI",
            f"3. Task will auto-close when complete"
        ]
    }
```

**Step 2: Test manually**

```bash
# Run with use_lokalise_translation=true
"Extract translations and use Lokalise auto-translation"
```

Expected: Keys created + translation task visible in Lokalise

**Step 3: Commit**

```bash
git add src/lokalise_mcp/server.py
git commit -m "feat: implement Lokalise auto-translation mode (Mode 2)"
```

---

## Task 7: Keep Mode 3 - Claude AI Translation (Existing)

**Files:**
- Modify: `src/lokalise_mcp/server.py:300-350`

**Step 1: Wrap existing translation code in Mode 3 check**

In `src/lokalise_mcp/server.py`:
```python
else:
    # Mode 3: Claude AI translation (existing behavior)
    if not has_anthropic:
        return {
            "status": "error",
            "message": "ANTHROPIC_API_KEY required for Claude AI translations. Use use_lokalise_translation=True for Lokalise's built-in translation instead."
        }

    # ... existing Claude translation code ...
    translator = AITranslator(api_key=config.anthropic_api_key)

    # ... rest of existing implementation ...
```

**Step 2: Test with Anthropic key**

```bash
# Set Anthropic key
export ANTHROPIC_API_KEY="your-key"

# Run tool
"Extract translations with AI"
```

Expected: Works exactly as before (Claude translations)

**Step 3: Commit**

```bash
git add src/lokalise_mcp/server.py
git commit -m "feat: preserve Claude AI translation as Mode 3"
```

---

## Task 8: Update Documentation

**Files:**
- Modify: `README.md` (Usage section)
- Modify: `docs/USAGE.md`

**Step 1: Update README with new modes**

In `README.md`, update the "How It Works" section:
```markdown
## How It Works

### Three Translation Modes

**Mode 1: No Translation (Fastest)**
- Set: No `ANTHROPIC_API_KEY`, `use_lokalise_translation=false`
- Creates keys with English text only
- You translate manually in Lokalise UI
- Free, fastest option

**Mode 2: Lokalise Auto-Translation (Recommended)**
- Set: No `ANTHROPIC_API_KEY`, `use_lokalise_translation=true`
- Creates keys, then creates Lokalise translation task
- Lokalise AI handles translations automatically
- Uses your Lokalise plan's translation credits
- Reuses translation memory

**Mode 3: Claude AI Translation**
- Set: `ANTHROPIC_API_KEY` provided
- Uses Claude to generate high-quality translations
- Best quality, costs Anthropic API usage
- Original behavior

### Example Usage

```bash
# Mode 1: Just create keys
"Create translation keys without AI"

# Mode 2: Use Lokalise auto-translation
"Create translation keys and use Lokalise auto-translation"

# Mode 3: Use Claude AI
"Create translation keys with Claude AI" # Requires ANTHROPIC_API_KEY
```
```

**Step 2: Update prerequisites**

Update README prerequisites to show Anthropic as optional:
```markdown
### Prerequisites

- Lokalise account with API access
- **Optional:** Anthropic API key (only for Claude AI translations)
```

**Step 3: Commit**

```bash
git add README.md docs/USAGE.md
git commit -m "docs: update documentation for three translation modes"
```

---

## Task 9: Update Environment Variable Template

**Files:**
- Modify: `.env.example` (create if doesn't exist)

**Step 1: Create/update .env.example**

Create `.env.example`:
```bash
# Lokalise Configuration (Required)
LOKALISE_API_TOKEN=your-lokalise-api-token
LOKALISE_PROJECT_ID=your-project-id

# Anthropic Configuration (Optional - only for Claude AI translations)
# ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional Configuration
DEFAULT_BASE_BRANCH=main
DEFAULT_BATCH_SIZE=3
ENABLE_SAFETY_CHECKS=true
```

**Step 2: Commit**

```bash
git add .env.example
git commit -m "docs: update env template to show Anthropic as optional"
```

---

## Task 10: Bump Version and Test

**Files:**
- Modify: `pyproject.toml`
- Test: Full integration test

**Step 1: Update version**

In `pyproject.toml`:
```toml
version = "0.2.0"  # Major feature: optional AI translations
```

**Step 2: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass

**Step 3: Test all three modes manually**

Test Mode 1:
```bash
unset ANTHROPIC_API_KEY
# Use MCP tool: "Create keys without AI"
```

Test Mode 2:
```bash
unset ANTHROPIC_API_KEY
# Use MCP tool: "Create keys with Lokalise auto-translation"
```

Test Mode 3:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Use MCP tool: "Create keys with Claude AI"
```

**Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0 - optional AI translations"
```

---

## Task 11: Update PHASE2_SUMMARY with Phase 5 Changes

**Files:**
- Create: `docs/PHASE5_SUMMARY.md`

**Step 1: Create Phase 5 summary**

Create comprehensive summary documenting:
- What changed
- Three translation modes
- Migration guide
- Breaking changes (none!)
- Benefits

**Step 2: Commit**

```bash
git add docs/PHASE5_SUMMARY.md
git commit -m "docs: add Phase 5 summary"
```

---

## Verification Checklist

After completing all tasks:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Mode 1 works (no translation)
- [ ] Mode 2 works (Lokalise auto-translation)
- [ ] Mode 3 works (Claude AI)
- [ ] README updated
- [ ] `.env.example` updated
- [ ] Version bumped to 0.2.0
- [ ] No breaking changes for existing users

## Expected Outcomes

1. **Existing users:** No changes needed, works exactly as before if they have `ANTHROPIC_API_KEY`
2. **New users:** Can use without Anthropic account
3. **Cost savings:** Users can choose free/included Lokalise translation
4. **Flexibility:** Three modes for different use cases

## Notes for Implementer

- Follow TDD strictly - test first, then implement
- Each task should take 5-15 minutes
- Commit after each task
- If a test fails unexpectedly, stop and debug before continuing
- Use @superpowers:verification-before-completion before marking complete
