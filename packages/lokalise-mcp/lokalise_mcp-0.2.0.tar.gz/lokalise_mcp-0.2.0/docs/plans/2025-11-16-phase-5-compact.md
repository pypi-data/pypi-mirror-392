# Phase 5: Optional AI Translations - Compact Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make Anthropic API key optional, add 3 translation modes (no AI, Lokalise AI, Claude AI)

**Architecture:** Make ANTHROPIC_API_KEY optional, add `use_lokalise_translation` parameter, implement three translation paths

**Tech Stack:** Python 3.11, FastMCP, python-lokalise-api, Anthropic SDK (optional)

---

## Task 1: Make Config Accept Optional Anthropic Key

**Files:**
- Modify: `src/lokalise_mcp/config.py:33-44`
- Test: `tests/test_config.py`

**TDD Steps:**

1. Write test: Config valid without Anthropic key
2. Run test (expect FAIL)
3. Remove Anthropic requirement from `validate()` method
4. Run test (expect PASS)
5. Commit: `feat: make Anthropic API key optional`

**Code:**
```python
# src/lokalise_mcp/config.py - validate() method
def validate(self) -> list[str]:
    errors = []
    if not self.lokalise_api_token:
        errors.append("LOKALISE_API_TOKEN is required")
    if not self.lokalise_project_id:
        errors.append("LOKALISE_PROJECT_ID is required")
    # ANTHROPIC_API_KEY now optional
    return errors
```

---

## Task 2: Add Lokalise Task Creation + Update Translator

**Files:**
- Modify: `src/lokalise_mcp/lokalise_client.py` (add method)
- Modify: `src/lokalise_mcp/translator.py:20-30`
- Test: `tests/test_lokalise_client.py`, `tests/test_translator.py`

**TDD Steps:**

1. Write test: `create_translation_task()` creates Lokalise task
2. Write test: Translator works without API key (returns empty dict)
3. Run tests (expect FAIL)
4. Implement `create_translation_task()` in LokaliseClient
5. Update AITranslator.__init__ to accept `api_key=None`
6. Update AITranslator.translate to return {} if no client
7. Run tests (expect PASS)
8. Commit: `feat: add Lokalise task creation and optional translator`

**Code:**
```python
# src/lokalise_mcp/lokalise_client.py
async def create_translation_task(
    self, key_ids: List[int], target_languages: List[str],
    task_title: str = "Auto-translate new keys"
) -> dict:
    languages = [{"language_iso": lang, "users": []}
                 for lang in target_languages if lang != self.base_language_iso]
    task_data = {
        "title": task_title,
        "task_type": "automatic_translation",
        "keys": key_ids,
        "languages": languages,
        "auto_close_task": True,
        "auto_close_items": True,
        "apply_ai_tm100_matches": True,
        "save_ai_translation_to_tm": True
    }
    return self.client.create_task(self.project_id, task_data)

# src/lokalise_mcp/translator.py
def __init__(self, api_key: str = None, model: str = DEFAULT_MODEL):
    self.api_key = api_key
    self.model = model
    self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

async def translate(self, context, target_languages):
    if not self.client:
        return {}
    # ... existing code ...
```

---

## Task 3: Implement Three Translation Modes in Server

**Files:**
- Modify: `src/lokalise_mcp/server.py:157-350`

**TDD Steps:**

1. Add `use_lokalise_translation: bool = False` parameter
2. Implement Mode 1 logic (no translation)
3. Implement Mode 2 logic (Lokalise task)
4. Wrap Mode 3 logic (Claude AI - existing)
5. Manual test all 3 modes
6. Commit: `feat: implement three translation modes`

**Code:**
```python
# src/lokalise_mcp/server.py
@mcp.tool()
async def extract_and_sync_translations(
    repo_path: Optional[str] = None,
    base_branch: str = "main",
    batch_size: int = 3,
    auto_approve: bool = False,
    skip_safety_check: bool = False,
    use_lokalise_translation: bool = False  # NEW
) -> Dict:
    """Three modes:
    1. No AI: Just create keys (no ANTHROPIC_API_KEY, use_lokalise_translation=False)
    2. Lokalise AI: Create keys + task (no ANTHROPIC_API_KEY, use_lokalise_translation=True)
    3. Claude AI: Use Claude (ANTHROPIC_API_KEY set)
    """
    config = get_config()
    has_anthropic = bool(config.anthropic_api_key)

    # ... extract keys ...

    if not has_anthropic and not use_lokalise_translation:
        # MODE 1: No translation
        for key in all_keys:
            if not await lokalise_client.get_key_by_name(key.key_name):
                await lokalise_client.create_key(
                    key_name=key.key_name,
                    platforms=["web"],
                    translations={base_language: key.default_text or key.key_name}
                )
        return {"status": "created_without_translation", ...}

    elif use_lokalise_translation:
        # MODE 2: Lokalise auto-translation
        created_keys = []
        for key in all_keys:
            if not await lokalise_client.get_key_by_name(key.key_name):
                response = await lokalise_client.create_key(...)
                created_keys.append({"key_id": response['key_id'], ...})

        if created_keys:
            task = await lokalise_client.create_translation_task(
                key_ids=[k['key_id'] for k in created_keys],
                target_languages=target_languages
            )
        return {"status": "created_with_lokalise_translation", "task_id": task['task_id'], ...}

    else:
        # MODE 3: Claude AI (existing)
        translator = AITranslator(api_key=config.anthropic_api_key)
        # ... existing Claude translation code ...
```

---

## Task 4: Update Documentation and Version

**Files:**
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `pyproject.toml`
- Create: `docs/PHASE5_SUMMARY.md`

**Steps:**

1. Update README: Add three modes explanation
2. Update README: Show Anthropic as optional
3. Update `.env.example`: Comment out Anthropic key
4. Bump version to `0.2.0`
5. Create Phase 5 summary document
6. Commit: `docs: update for optional AI translations v0.2.0`

**README Updates:**
```markdown
### Three Translation Modes

**Mode 1: No Translation** - Just create keys
**Mode 2: Lokalise Auto-Translation** - Create keys + Lokalise task (recommended)
**Mode 3: Claude AI** - Use Claude for translations (requires ANTHROPIC_API_KEY)

### Prerequisites
- Lokalise account
- **Optional:** Anthropic API key (only for Mode 3)
```

---

## Task 5: Test All Modes and Verify

**Steps:**

1. Run pytest: `pytest tests/ -v`
2. Test Mode 1: Unset ANTHROPIC_API_KEY, create keys
3. Test Mode 2: Unset ANTHROPIC_API_KEY, use Lokalise translation
4. Test Mode 3: Set ANTHROPIC_API_KEY, use Claude
5. Verify no breaking changes for existing users
6. Commit: `test: verify all three translation modes`

**Manual Tests:**
```bash
# Mode 1
unset ANTHROPIC_API_KEY
"Create translation keys without AI"

# Mode 2
"Create translation keys with Lokalise auto-translation"

# Mode 3
export ANTHROPIC_API_KEY="sk-ant-..."
"Create translation keys with Claude AI"
```

---

## Verification Checklist

- [ ] Task 1: Config accepts optional Anthropic (tests pass)
- [ ] Task 2: Lokalise task + translator work (tests pass)
- [ ] Task 3: All 3 modes implemented (manual test)
- [ ] Task 4: Docs updated, version bumped
- [ ] Task 5: All tests pass, all modes work
- [ ] No breaking changes for existing users
