# Lokalise MCP - Installation Guide

This guide will help you install and configure the Lokalise MCP server.

## Prerequisites

- Python 3.10 or higher
- Git repository with translation keys
- Lokalise account with API access
- Anthropic API key (for AI translations)

## Installation Steps

### 1. Clone or Download

```bash
git clone <repository-url>
cd lokalise-assist
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

For development (includes testing tools):
```bash
pip install -e ".[dev]"
```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Lokalise Configuration
LOKALISE_API_TOKEN=your_lokalise_api_token_here
LOKALISE_PROJECT_ID=your_project_id_here

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional Configuration
DEFAULT_BASE_BRANCH=main
DEFAULT_BATCH_SIZE=3
ENABLE_SAFETY_CHECKS=true
```

#### Getting Your Lokalise API Token

1. Log in to [Lokalise](https://lokalise.com)
2. Go to your profile settings
3. Navigate to **API Tokens**
4. Create a new token with **Read/Write** permissions
5. Copy the token to your `.env` file

#### Getting Your Lokalise Project ID

1. Open your project in Lokalise
2. Look at the URL: `https://app.lokalise.com/project/{PROJECT_ID}`
3. Copy the project ID to your `.env` file

#### Getting Your Anthropic API Key

1. Sign up at [Anthropic Console](https://console.anthropic.com)
2. Navigate to **API Keys**
3. Create a new API key
4. Copy it to your `.env` file

### 5. Configure Project Settings (Optional)

Create a `.lokalise-mcp.json` file in your project root:

```json
{
  "projectId": "your_project_id",
  "baseBranch": "main",
  "batchSize": 3,
  "filePatterns": ["**/*.tsx", "**/*.ts", "**/*.jsx"],
  "excludePatterns": ["**/node_modules/**", "**/dist/**"],
  "safety": {
    "enabled": true,
    "customBlocklist": []
  }
}
```

This file allows you to customize:
- Which file extensions to scan
- Which directories to exclude
- Batch size for creating keys
- Safety check configuration

### 6. Add to Claude Desktop

To use this MCP server with Claude Desktop, add it to your Claude configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lokalise": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "lokalise_mcp.server"],
      "env": {
        "LOKALISE_API_TOKEN": "your_token",
        "LOKALISE_PROJECT_ID": "your_project_id",
        "ANTHROPIC_API_KEY": "your_key"
      }
    }
  }
}
```

Replace `/path/to/venv/bin/python` with the actual path to your virtual environment's Python.

### 7. Verify Installation

Test that everything is working:

```bash
python -c "from lokalise_mcp.config import load_config; c = load_config(); print('Config loaded successfully')"
```

You should see: `Config loaded successfully`

## Troubleshooting

### "ModuleNotFoundError"

Make sure you've activated your virtual environment:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### "Configuration errors: LOKALISE_API_TOKEN is required"

Ensure your `.env` file exists and contains all required variables.

### Git Repository Not Found

Make sure you're running the MCP tools from within a git repository.

## Next Steps

Once installed, proceed to the [Usage Guide](USAGE.md) to learn how to use the MCP server.
