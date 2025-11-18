"""Lokalise MCP Server - Main entry point."""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from fastmcp import FastMCP

from .config import Config, load_config
from .git_utils import GitDiffExtractor
from .key_extractor import KeyExtractor, TranslationKey
from .lokalise_client import LokaliseClient
from .translator import AITranslator, TranslationContext
from .safety import SafetyGuard

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("Lokalise Translation Sync")

# Global config (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or load configuration."""
    global _config
    if _config is None:
        _config = load_config()
        errors = _config.validate()
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    return _config


@mcp.resource("lokalise://config")
def get_mcp_config() -> Dict:
    """Get current MCP configuration."""
    config = get_config()
    return {
        "project_id": config.lokalise_project_id,
        "api_token_set": bool(config.lokalise_api_token),
        "default_base_branch": config.default_base_branch,
        "default_batch_size": config.default_batch_size,
        "safety_checks_enabled": config.enable_safety_checks,
    }


@mcp.tool()
async def get_lokalise_project_info() -> Dict:
    """Get information about the Lokalise project configuration.

    Returns project details including configured languages and key count.
    """
    config = get_config()
    client = LokaliseClient(config.lokalise_api_token, config.lokalise_project_id)

    project_info = await client.get_project_info()
    languages = await client.get_project_languages()

    return {
        "project_id": project_info["project_id"],
        "project_name": project_info["name"],
        "base_language": project_info["base_lang_iso"],
        "languages": [
            {
                "code": lang["lang_iso"],
                "name": lang["lang_name"],
                "is_base": lang["lang_iso"] == project_info["base_lang_iso"]
            }
            for lang in languages
        ],
        "total_languages": len(languages)
    }


@mcp.tool()
async def preview_new_keys(
    repo_path: Optional[str] = None,
    base_branch: str = "main"
) -> Dict:
    """Preview translation keys that would be extracted without creating them.

    Args:
        repo_path: Path to your project's git repository. Defaults to current working directory.
        base_branch: Git branch to compare against (default: main)

    Returns:
        Dictionary with extracted keys grouped by namespace
    """
    config = get_config()

    if repo_path is None:
        repo_path = os.getcwd()

    # Extract changed files
    git_extractor = GitDiffExtractor(
        repo_path=repo_path,
        file_patterns=config.file_patterns,
        exclude_patterns=config.exclude_patterns
    )

    changed_files = git_extractor.get_changed_files(base_branch)

    # Extract keys from changed files
    key_extractor = KeyExtractor(
        translation_functions=config.translation_functions,
        default_param=config.default_param_name
    )

    all_keys = []
    for file_path in changed_files:
        keys = key_extractor.extract_from_file(file_path)
        all_keys.extend(keys)

    # Group by namespace
    namespaces = {}
    missing_defaults = []

    for key in all_keys:
        # Extract namespace (first part of key)
        namespace = key.key_name.split('.')[0]

        if namespace not in namespaces:
            namespaces[namespace] = []

        namespaces[namespace].append({
            "key": key.key_name,
            "default": key.default_text,
            "file": key.file_path,
            "line": key.line_number,
            "has_default": key.default_text is not None
        })

        if key.default_text is None:
            missing_defaults.append(key)

    return {
        "total_keys": len(all_keys),
        "namespaces": namespaces,
        "missing_defaults": [
            {
                "key": k.key_name,
                "file": k.file_path,
                "line": k.line_number,
                "context": k.context[:100] + "..." if len(k.context) > 100 else k.context
            }
            for k in missing_defaults
        ],
        "changed_files": [str(f) for f in changed_files]
    }


@mcp.tool()
async def extract_and_sync_translations(
    repo_path: Optional[str] = None,
    base_branch: str = "main",
    batch_size: int = 3,
    auto_approve: bool = False,
    skip_safety_check: bool = False,
    use_lokalise_translation: bool = False
) -> Dict:
    """Extract translation keys from git diff and sync to Lokalise.

    Three translation modes:
    1. No AI Translation: Just create keys with base language text only.
       (No ANTHROPIC_API_KEY, use_lokalise_translation=False)
       - Fastest, free option
       - No translations generated

    2. Lokalise AI Translation: Create keys + Lokalise auto-translation task.
       (No ANTHROPIC_API_KEY, use_lokalise_translation=True)
       - Uses Lokalise's built-in AI for translations
       - Creates translation task in Lokalise

    3. Claude AI Translation: Use Claude to generate translations.
       (ANTHROPIC_API_KEY set)
       - Highest quality translations
       - Translations created immediately with keys

    Workflow:
    1. Extract keys from changed files
    2. Check for safety issues (if enabled and Claude available)
    3. Generate translations (based on mode)
    4. Preview and request approval (unless auto_approve=True)
    5. Create keys in Lokalise (in batches for Mode 3, individually for Modes 1&2)

    Args:
        repo_path: Path to your project's git repository. Defaults to current working directory.
        base_branch: Git branch to compare against (default: main)
        batch_size: Number of keys to create per batch (default: 3, only for Mode 3)
        auto_approve: Skip approval prompts and create all keys (default: False)
        skip_safety_check: Skip content safety checks (default: false)
        use_lokalise_translation: Use Lokalise AI translation instead of no translation (default: False)

    Returns:
        Summary with created/skipped/failed counts
    """
    config = get_config()

    if repo_path is None:
        repo_path = os.getcwd()

    # Detect translation mode
    has_anthropic = bool(config.anthropic_api_key)

    # Initialize core services (always needed)
    git_extractor = GitDiffExtractor(
        repo_path=repo_path,
        file_patterns=config.file_patterns,
        exclude_patterns=config.exclude_patterns
    )

    key_extractor = KeyExtractor(
        translation_functions=config.translation_functions,
        default_param=config.default_param_name
    )

    lokalise_client = LokaliseClient(
        config.lokalise_api_token,
        config.lokalise_project_id
    )

    # Initialize AI services only if Claude is available (Mode 3)
    translator = None
    safety_guard = None

    if has_anthropic:
        translator = AITranslator(config.anthropic_api_key)
        safety_guard = SafetyGuard(
            config.anthropic_api_key,
            use_ai_check=config.enable_safety_checks and not skip_safety_check
        )

    # Step 1: Extract keys
    changed_files = git_extractor.get_changed_files(base_branch)
    all_keys = []

    for file_path in changed_files:
        keys = key_extractor.extract_from_file(file_path)
        all_keys.extend(keys)

    if not all_keys:
        return {
            "status": "no_keys_found",
            "message": "No translation keys found in changed files"
        }

    # Step 2: Safety check (only in Mode 3 - Claude AI)
    flagged_keys = []

    if has_anthropic and not skip_safety_check and config.enable_safety_checks:
        for key in all_keys:
            if key.default_text:
                safety_result = await safety_guard.check_source_text(key.default_text)
                if not safety_result.is_safe:
                    flagged_keys.append({
                        "key": key.key_name,
                        "text": key.default_text,
                        "flags": safety_result.flags,
                        "reason": safety_result.reason
                    })

    # Step 3: Get languages and project info from Lokalise
    languages = await lokalise_client.get_project_languages()
    project_info = await lokalise_client.get_project_info()
    base_language = project_info["base_lang_iso"]

    # MODE 1: No AI Translation - just create keys with base language
    if not has_anthropic and not use_lokalise_translation:
        total_created = 0
        total_skipped = 0
        total_failed = 0
        all_errors = []

        for key in all_keys:
            if key.default_text is None:
                # Skip keys without default text
                total_skipped += 1
                continue

            # Check if key already exists
            existing_key = await lokalise_client.get_key_by_name(key.key_name)
            if existing_key:
                total_skipped += 1
                continue

            try:
                # Create key with base language only
                await lokalise_client.create_key(
                    key_name=key.key_name,
                    platforms=["web"],
                    translations={base_language: key.default_text}
                )
                total_created += 1
            except Exception as e:
                total_failed += 1
                all_errors.append(f"{key.key_name}: {str(e)}")

        return {
            "status": "created_without_translation",
            "mode": "no_ai",
            "message": "Keys created with base language text only. No translations generated.",
            "total_keys_found": len(all_keys),
            "created": total_created,
            "skipped": total_skipped,
            "failed": total_failed,
            "errors": all_errors,
            "base_language": base_language
        }

    # MODE 2: Lokalise AI Translation - create keys then translation task
    elif not has_anthropic and use_lokalise_translation:
        total_created = 0
        total_skipped = 0
        total_failed = 0
        all_errors = []
        created_key_ids = []

        for key in all_keys:
            if key.default_text is None:
                # Skip keys without default text
                total_skipped += 1
                continue

            # Check if key already exists
            existing_key = await lokalise_client.get_key_by_name(key.key_name)
            if existing_key:
                total_skipped += 1
                continue

            try:
                # Create key with base language only
                result = await lokalise_client.create_key(
                    key_name=key.key_name,
                    platforms=["web"],
                    translations={base_language: key.default_text}
                )
                total_created += 1
                created_key_ids.append(result["key_id"])
            except Exception as e:
                total_failed += 1
                all_errors.append(f"{key.key_name}: {str(e)}")

        # Get target languages (exclude base language)
        target_languages = [
            lang["lang_iso"]
            for lang in languages
            if lang["lang_iso"] != base_language
        ]

        # Initialize task variables
        task_id = None
        task_status = None

        # Create translation task if we created any keys
        if created_key_ids:
            try:
                task = await lokalise_client.create_translation_task(
                    key_ids=created_key_ids,
                    target_languages=target_languages,
                    task_title=f"Auto-translate {len(created_key_ids)} new keys"
                )
                task_id = task.task_id
                task_status = "created"
            except Exception as e:
                task_status = "failed"
                all_errors.append(f"Translation task creation failed: {str(e)}")

        return {
            "status": "created_with_lokalise_translation",
            "mode": "lokalise_ai",
            "message": f"Keys created and Lokalise translation task initiated for {len(target_languages)} languages.",
            "total_keys_found": len(all_keys),
            "created": total_created,
            "skipped": total_skipped,
            "failed": total_failed,
            "errors": all_errors,
            "base_language": base_language,
            "target_languages": target_languages,
            "task_id": task_id,
            "task_status": task_status
        }

    # MODE 3: Claude AI Translation - existing behavior
    else:
        # Step 4: Translate keys using Claude
        translations_to_create = []

        for key in all_keys:
            if key.default_text is None:
                # TODO: In future, prompt user for default
                continue

            key_translations = {base_language: key.default_text}

            # Translate to other languages
            context = TranslationContext(
                key_name=key.key_name,
                source_text=key.default_text,
                code_context=key.context,
                file_path=key.file_path,
                parameters=key.parameters
            )

            for lang in languages:
                if lang["lang_iso"] == base_language:
                    continue

                translation = await translator.translate(context, lang["lang_name"])

                # Verify translation safety
                if not skip_safety_check and config.enable_safety_checks:
                    trans_check = await safety_guard.check_translation(
                        key.default_text,
                        translation,
                        lang["lang_name"]
                    )

                    if not trans_check.is_safe:
                        continue  # Skip this translation

                key_translations[lang["lang_iso"]] = translation

            translations_to_create.append({
                "key_name": key.key_name,
                "translations": key_translations
            })

        # Step 5: Create in Lokalise (batched)
        total_created = 0
        total_skipped = 0
        total_failed = 0
        all_errors = []

        # Split into batches
        for i in range(0, len(translations_to_create), batch_size):
            batch = translations_to_create[i:i+batch_size]

            # TODO: In future, show preview and ask for approval here

            result = await lokalise_client.create_keys(batch)

            total_created += result["created"]
            total_skipped += result["skipped"]
            total_failed += result["failed"]
            all_errors.extend(result["errors"])

        return {
            "status": "completed",
            "mode": "claude_ai",
            "message": "Keys created with Claude AI translations.",
            "total_keys_found": len(all_keys),
            "created": total_created,
            "skipped": total_skipped,
            "failed": total_failed,
            "flagged_keys": flagged_keys,
            "errors": all_errors,
            "languages": [lang["lang_iso"] for lang in languages]
        }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
