# Phase 5: Optional AI Translations + Lokalise Auto-Translation

**Date:** 2025-11-16
**Goal:** Make Anthropic API key optional and leverage Lokalise's built-in auto-translation

## Problem

Currently:
- ANTHROPIC_API_KEY is required
- Users pay for Anthropic API calls
- Lokalise already has built-in AI translation that users might prefer
- Some users just want to create keys and translate manually

## Solution

Make Anthropic optional and add Lokalise auto-translation support.

### Three Translation Modes

**Mode 1: No AI Translation (Just create keys)**
- ANTHROPIC_API_KEY not provided
- `use_lokalise_translation: false` (default)
- Creates keys with only the default English text
- Fastest, free, users translate manually in Lokalise UI

**Mode 2: Lokalise Auto-Translation**
- ANTHROPIC_API_KEY not provided
- `use_lokalise_translation: true`
- Creates keys, then creates an "automatic_translation" task in Lokalise
- Uses Lokalise's built-in AI (Google Translate, DeepL, or Lokalise AI)
- Cost depends on Lokalise plan

**Mode 3: Claude AI Translation (Current behavior)**
- ANTHROPIC_API_KEY provided
- Uses Claude to generate translations
- Most expensive, highest quality

## API Research

### Lokalise Tasks API

Create automatic translation task:
```python
POST /api2/projects/{project_id}/tasks

{
  "title": "Auto-translate new keys",
  "task_type": "automatic_translation",  # KEY: This triggers Lokalise AI
  "keys": [key_id_1, key_id_2, ...],
  "languages": [
    {"language_iso": "no", "users": []},  # Norwegian
    {"language_iso": "ne", "users": []}   # Nepali
  ],
  "auto_close_task": true,  # Auto-close when done
  "auto_close_items": true
}
```

### Benefits of Lokalise Auto-Translation

✅ No Anthropic API key needed
✅ Uses Lokalise's translation memory (reuses past translations)
✅ Integrated with user's Lokalise plan
✅ Supports multiple providers (Google, DeepL, Lokalise AI)
✅ Can apply TM100 matches (exact matches from translation memory)

## Implementation Plan

### 1. Make Anthropic API Key Optional

**File:** `src/lokalise_mcp/config.py`

Change validation:
```python
def validate(self) -> list[str]:
    """Validate required configuration."""
    errors = []

    if not self.lokalise_api_token:
        errors.append("LOKALISE_API_TOKEN is required")
    if not self.lokalise_project_id:
        errors.append("LOKALISE_PROJECT_ID is required")
    # ANTHROPIC_API_KEY is now optional - only warn if using AI translation

    return errors
```

### 2. Update Translator to Handle Missing API Key

**File:** `src/lokalise_mcp/translator.py`

Add check:
```python
class AITranslator:
    def __init__(self, api_key: str = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.model = model
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None  # No AI translation available

    def translate_batch(self, ...):
        if not self.client:
            # Return empty translations
            return {lang: "" for lang in target_languages}
        # ... existing code
```

### 3. Add Lokalise Task Creation

**File:** `src/lokalise_mcp/lokalise_client.py`

Add new method:
```python
async def create_translation_task(
    self,
    key_ids: List[int],
    target_languages: List[str],
    task_title: str = "Auto-translate new keys"
) -> dict:
    """Create an automatic translation task in Lokalise.

    This triggers Lokalise's built-in AI translation (Google/DeepL/Lokalise AI).
    """
    # Get language objects
    languages = [
        {"language_iso": lang, "users": []}
        for lang in target_languages
        if lang != self.base_language_iso  # Don't translate base language
    ]

    task_data = {
        "title": task_title,
        "task_type": "automatic_translation",
        "keys": key_ids,
        "languages": languages,
        "auto_close_task": True,
        "auto_close_items": True,
        "apply_ai_tm100_matches": True,  # Reuse translation memory
        "save_ai_translation_to_tm": True  # Save to TM for future
    }

    response = self.client.create_task(self.project_id, task_data)
    return response
```

### 4. Update Main Workflow

**File:** `src/lokalise_mcp/server.py`

Update `extract_and_sync_translations`:
```python
@mcp.tool()
async def extract_and_sync_translations(
    repo_path: Optional[str] = None,
    base_branch: str = "main",
    batch_size: int = 3,
    auto_approve: bool = False,
    skip_safety_check: bool = False,
    use_lokalise_translation: bool = False  # NEW PARAMETER
) -> Dict:
    """Extract translation keys from git diff and sync to Lokalise.

    Translation modes:
    - If ANTHROPIC_API_KEY provided: Use Claude AI for translations
    - If use_lokalise_translation=True: Create Lokalise auto-translation task
    - Otherwise: Just create keys without translations

    Args:
        ...
        use_lokalise_translation: Create Lokalise auto-translation task (default: False)
    """
    config = get_config()

    # Determine translation mode
    has_anthropic = bool(config.anthropic_api_key)

    # ... extract keys ...

    if has_anthropic:
        # Mode 3: Use Claude AI (existing behavior)
        translator = AITranslator(api_key=config.anthropic_api_key)
        # ... generate translations ...

    elif use_lokalise_translation:
        # Mode 2: Use Lokalise auto-translation
        # Create keys first (without translations)
        created_key_ids = []
        for key in keys_to_create:
            created = await lokalise_client.create_key(
                key_name=key.key_name,
                platforms=["web"],
                translations={
                    base_language: key.default_text or key.key_name
                }
            )
            created_key_ids.append(created['key_id'])

        # Create automatic translation task
        task = await lokalise_client.create_translation_task(
            key_ids=created_key_ids,
            target_languages=target_languages
        )

        return {
            "status": "created_with_lokalise_translation",
            "created_count": len(created_key_ids),
            "task_id": task['task_id'],
            "message": f"Created {len(created_key_ids)} keys and Lokalise translation task"
        }

    else:
        # Mode 1: Just create keys (no translation)
        for key in keys_to_create:
            await lokalise_client.create_key(
                key_name=key.key_name,
                platforms=["web"],
                translations={
                    base_language: key.default_text or key.key_name
                }
            )

        return {
            "status": "created_without_translation",
            "created_count": len(keys_to_create),
            "message": "Created keys. Translate manually in Lokalise UI."
        }
```

## Updated Configuration

### Environment Variables

```bash
# Required
LOKALISE_API_TOKEN=your-token
LOKALISE_PROJECT_ID=your-project-id

# Optional (for Claude AI translations)
ANTHROPIC_API_KEY=your-key  # Can be omitted now!
```

### Usage Examples

**Example 1: Just create keys (no translation)**
```
"Create translation keys without AI translation"
# Creates keys, user translates in Lokalise UI
```

**Example 2: Use Lokalise auto-translation**
```
"Create translation keys and use Lokalise auto-translation"
# Creates keys + Lokalise translation task
```

**Example 3: Use Claude AI (if API key provided)**
```
"Create translation keys with AI translation"
# Uses Claude to generate translations (existing behavior)
```

## Benefits

1. **Lower barrier to entry** - No Anthropic account needed
2. **Cost savings** - Use Lokalise's included AI translation
3. **Flexibility** - Three modes to choose from
4. **Translation memory** - Lokalise reuses past translations
5. **Simpler setup** - One less API key to configure

## Testing Strategy

1. Test Mode 1: No API keys, just create keys
2. Test Mode 2: No Anthropic key, use Lokalise task
3. Test Mode 3: With Anthropic key, use Claude
4. Verify task creation in Lokalise UI
5. Check if translations appear after task completes

## Documentation Updates

- Update README to show Anthropic as optional
- Add examples for each translation mode
- Document `use_lokalise_translation` parameter
- Show cost comparison between modes

## Migration Path

Existing users:
- No breaking changes
- If they have ANTHROPIC_API_KEY set, behavior is unchanged
- New users can skip Anthropic entirely

## Future Enhancements

- Webhook support to notify when Lokalise translation completes
- Option to choose translation provider (Google/DeepL/Lokalise AI)
- Hybrid mode: Claude for some languages, Lokalise for others
- Translation quality comparison between Claude and Lokalise
