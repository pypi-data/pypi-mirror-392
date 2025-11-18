# Lokalise MCP Integration

MCP server for extracting translation keys from code and syncing them to Lokalise with AI-powered translations.

## Features

- 🔍 Extract translation keys from git diff and untracked files
- 🤖 Three translation modes: No AI, Lokalise AI, or Claude AI
- 👀 Interactive preview before creating keys
- 🛡️ Content safety guards to prevent harmful translations
- 📦 Batch creation with progress tracking (3 keys at a time)
- ⚠️ Skip existing keys automatically
- 🎯 Supports custom translation functions (t, translate, Translate, etc.)

## Installation

### Prerequisites

- Lokalise account with API access
- **Optional:** Anthropic API key (only required for Mode 3 - Claude AI translations)
- **One of:**
  - Docker (for Option 1 - easiest, no Python required)
  - Python 3.10+ with uv/pip (for Options 2-3)

### Option 1: Using uvx (Recommended - Simplest Setup)

No installation needed - just works:

Configure Claude Code MCP in `~/.config/claude/config.json`:
```json
{
  "mcpServers": {
    "lokalise": {
      "command": "uvx",
      "args": ["lokalise-mcp"],
      "env": {
        "LOKALISE_API_TOKEN": "your-api-token-here",
        "LOKALISE_PROJECT_ID": "your-project-id-here"
      }
    }
  }
}
```

**Note:** Add `"ANTHROPIC_API_KEY": "your-anthropic-api-key-here"` only if you want Mode 3 (Claude AI translations).

**Benefits:**
- ✅ Zero configuration - just 2 required environment variables
- ✅ Auto-updates to latest version
- ✅ No volume mounts or file path complexity
- ✅ Works immediately

### Option 2: Using Docker (Alternative - No Python Required)

Docker is available but more complex because the container needs access to your local git repository:

```bash
docker pull sidzan/lokalise-mcp:latest
```

Note: Docker setup for this MCP is more complex than API-only MCPs (like mcp-atlassian) because lokalise-mcp needs to read your local git repository files. **We recommend using uvx (Option 1) instead for simplicity.**

If you still want Docker, the image is available at `sidzan/lokalise-mcp:latest`.

### Option 3: Install Globally with pip/uv

If you prefer to install the package:

```bash
# Using pip
pip install lokalise-mcp

# Or using uv
uv tool install lokalise-mcp
```

Then configure Claude Code:
```json
{
  "mcpServers": {
    "lokalise": {
      "command": "lokalise-mcp",
      "env": {
        "LOKALISE_API_TOKEN": "your-api-token-here",
        "LOKALISE_PROJECT_ID": "your-project-id-here"
      }
    }
  }
}
```

**Note:** Add `"ANTHROPIC_API_KEY": "your-anthropic-api-key-here"` only if you want Mode 3 (Claude AI translations).

### Option 4: Install from Source (For Development)

```bash
git clone <your-repo-url>
cd lokalise-assist
uv tool install .
```

Then use the same configuration as Option 2.

### Configuration

You can customize extraction patterns in `.lokalise-mcp.json` in your project directory:

```json
{
  "baseBranch": "main",
  "batchSize": 3,
  "filePatterns": ["**/*.tsx", "**/*.ts", "**/*.jsx", "**/*.js"],
  "excludePatterns": ["**/node_modules/**", "**/dist/**"],
  "translationPatterns": {
    "functions": ["t", "translate", "Translate"],
    "defaultParam": "_"
  },
  "safety": {
    "enabled": true
  }
}
```

## Three Translation Modes

lokalise-mcp now supports three translation modes to fit different workflows and budgets:

### Mode 1: No Translation - Just create keys
- No AI translation at all
- Creates keys with base language text only
- Fastest and completely free
- Users translate manually in Lokalise UI
- **Use when:** You prefer manual translation or have your own workflow

### Mode 2: Lokalise Auto-Translation (Recommended)
- Creates keys + Lokalise auto-translation task
- Uses Lokalise's built-in AI (Google Translate, DeepL, or Lokalise AI)
- Integrated with your Lokalise plan
- Reuses translation memory for consistency
- **Use when:** You want AI translation without extra API costs

### Mode 3: Claude AI Translation
- Uses Claude (claude-3-5-haiku) for high-quality translations
- Requires ANTHROPIC_API_KEY
- Includes content safety checks
- Most expensive but highest quality
- **Use when:** You need premium translation quality

### Usage Examples

**Mode 1: No Translation**
```
"Create translation keys without AI translation"
```

**Mode 2: Lokalise AI (set use_lokalise_translation=true)**
```
"Create translation keys and use Lokalise auto-translation"
```

**Mode 3: Claude AI (requires ANTHROPIC_API_KEY)**
```
"Create translation keys with AI translation"
```

## Quick Start

1. **Install** following the steps above
2. **Configure** your API keys in the MCP server config
3. **Use** the tools in Claude Code by typing commands like:
   - "Preview translation keys from my changes"
   - "Extract and sync translations to Lokalise"

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Setup and configuration
- [Usage Guide](docs/USAGE.md) - How to use the MCP tools
- [Implementation Plan](docs/plans/2025-11-15-lokalise-mcp-integration.md) - Technical details

## Usage

### Available MCP Tools

#### 1. `get_lokalise_project_info`
Get project details including configured languages.

**Example usage in Claude Code:**
```
"Show me my Lokalise project info"
```

#### 2. `preview_new_keys`
Preview translation keys that would be extracted without creating them (dry run).

**Parameters:**
- `repo_path` (optional): Path to your project repository. **Defaults to current working directory.**
- `base_branch` (optional): Branch to compare against (default: "main")

**Example usage in Claude Code:**
```
"Preview translation keys"
```

#### 3. `extract_and_sync_translations`
Extract keys from changed/untracked files and create them in Lokalise with AI translations.

**Parameters:**
- `repo_path` (optional): Path to your project repository. **Defaults to current working directory.**
- `base_branch` (optional): Branch to compare against (default: "main")
- `batch_size` (optional): Number of keys to create per batch (default: 3)
- `auto_approve` (optional): Skip approval prompts (default: false)
- `skip_safety_check` (optional): Skip content safety checks (default: false)

**Example usage in Claude Code:**
```
"Extract and sync translations to Lokalise"
```

## How It Works

1. **Extract**: Scans files changed in your branch AND untracked files for translation patterns:
   - `t('key', { _: 'Default Text' })`
   - `translate('key', { _: 'Default Text' })`
   - `Translate('key', { _: 'Default Text' })`
   - Or any custom function you configure

2. **Translate**: Uses Claude AI (claude-3-5-haiku) to generate natural translations for all project languages

3. **Verify**: Runs safety checks (regex + AI) to prevent harmful/abusive content

4. **Create**: Adds keys to Lokalise in batches of 3, skipping duplicates automatically

## Supported Translation Patterns

The server detects these patterns by default:

```javascript
// With default text
t("products.title", { _: "Products" })
translate("users.greeting", { _: "Hello" })
Translate("app.welcome", { _: "Welcome!" })

// Without default (will prompt or skip)
t("products.subtitle")
```

You can customize the function names and default parameter in `.lokalise-mcp.json`.

## License

MIT
