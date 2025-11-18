# PyPI Package Distribution - Design

**Date:** 2025-11-15
**Status:** Implementation Ready
**Goal:** Make lokalise-mcp globally installable without manual path configuration

## Problem

Current installation is cumbersome:
1. Users must clone repository
2. MCP config requires absolute paths
3. Manual environment setup in multiple locations
4. Not discoverable or easy to update

## Solution: Publish to PyPI

Distribute as a standard Python package that can be installed globally.

### Installation Methods

**Method 1: uvx (recommended - no install needed)**
```bash
# In MCP config
{
  "command": "uvx",
  "args": ["--from", "lokalise-mcp", "lokalise-mcp"],
  "env": { ... }
}
```

**Method 2: pip/uv install**
```bash
pip install lokalise-mcp
# or
uv tool install lokalise-mcp

# In MCP config
{
  "command": "lokalise-mcp",
  "env": { ... }
}
```

## Architecture Changes

### 1. Package Structure
```
lokalise-mcp/
├── src/
│   └── lokalise_mcp/
│       ├── __init__.py
│       ├── __main__.py      # NEW: CLI entry point
│       ├── server.py
│       └── ...
├── pyproject.toml           # UPDATE: Add entry points
└── README.md                # UPDATE: Installation docs
```

### 2. Entry Point

Add to `pyproject.toml`:
```toml
[project.scripts]
lokalise-mcp = "lokalise_mcp.__main__:main"
```

Create `src/lokalise_mcp/__main__.py`:
```python
"""CLI entry point for lokalise-mcp."""
from .server import main

if __name__ == "__main__":
    main()
```

### 3. PyPI Metadata

Update `pyproject.toml`:
- Add description, keywords, classifiers
- Set version to 0.1.0
- Add repository URLs
- Add author info
- Ensure all dependencies listed

### 4. Environment Variables

Keep existing .env support but document that MCP config env takes precedence.

## Implementation Steps

1. **Update pyproject.toml**
   - Add [project.scripts] entry point
   - Add PyPI metadata (description, keywords, classifiers)
   - Verify dependencies are correct
   - Set version 0.1.0

2. **Create __main__.py**
   - Simple wrapper that calls server.main()
   - Allows both `python -m lokalise_mcp` and `lokalise-mcp` command

3. **Test locally**
   - `uv tool install .` (from repo directory)
   - Verify `lokalise-mcp` command works
   - Test with MCP config using command name

4. **Test with uvx**
   - Build package: `uv build`
   - Test local install: `uvx ./dist/lokalise_mcp-0.1.0-py3-none-any.whl`

5. **Publish to Test PyPI**
   - Create account on test.pypi.org
   - `uv publish --publish-url https://test.pypi.org/legacy/`
   - Test install: `uvx --from https://test.pypi.org/simple/ lokalise-mcp`

6. **Publish to PyPI**
   - Create account on pypi.org
   - `uv publish`
   - Test install: `uvx lokalise-mcp`

7. **Update Documentation**
   - README.md with new installation
   - INSTALLATION.md
   - Add troubleshooting section

## MCP Configuration

### Before (Manual Clone)
```json
{
  "lokalise": {
    "command": "/Users/username/.local/bin/uv",
    "args": ["--directory", "/absolute/path/to/lokalise-assist", "run", "python", "-m", "lokalise_mcp.server"],
    "env": { ... }
  }
}
```

### After (uvx - recommended)
```json
{
  "lokalise": {
    "command": "uvx",
    "args": ["--from", "lokalise-mcp", "lokalise-mcp"],
    "env": {
      "LOKALISE_API_TOKEN": "...",
      "LOKALISE_PROJECT_ID": "...",
      "ANTHROPIC_API_KEY": "..."
    }
  }
}
```

### After (pip install)
```json
{
  "lokalise": {
    "command": "lokalise-mcp",
    "env": {
      "LOKALISE_API_TOKEN": "...",
      "LOKALISE_PROJECT_ID": "...",
      "ANTHROPIC_API_KEY": "..."
    }
  }
}
```

## Benefits

1. **Zero-path configuration** - No absolute paths needed
2. **Easy discovery** - `pip search lokalise-mcp`
3. **Easy updates** - `pip install --upgrade lokalise-mcp` or uvx auto-updates
4. **Cross-platform** - Works anywhere Python works
5. **Standard practice** - Follows Python ecosystem norms
6. **Development mode** - Can still use `uv tool install .` for local dev

## Testing Strategy

1. Local install test with `uv tool install .`
2. Command execution test: `lokalise-mcp` should start server
3. MCP integration test with Claude Code
4. Test PyPI install before production PyPI
5. Version update test

## Rollout

1. Publish 0.1.0 to Test PyPI
2. Test with real MCP config
3. Fix any issues
4. Publish 0.1.0 to production PyPI
5. Update README and docs
6. Announce in relevant communities

## Future Enhancements

- CI/CD for automated publishing
- Homebrew formula for Mac users
- Chocolatey package for Windows
- Pre-built binaries with PyInstaller
- Auto-update checking
