# Publishing Guide

This guide explains how to publish lokalise-mcp to PyPI.

## Prerequisites

1. PyPI account: https://pypi.org/account/register/
2. Test PyPI account (optional but recommended): https://test.pypi.org/account/register/
3. API tokens for both (Settings → API tokens)

## Configure uv for Publishing

```bash
# Add PyPI token
export UV_PUBLISH_TOKEN="your-pypi-token-here"

# Or for Test PyPI
export UV_PUBLISH_TOKEN="your-test-pypi-token-here"
```

## Publishing Steps

### 1. Test Locally First

```bash
# Build the package
uv build

# Install locally to test
uv tool install --force .

# Verify the command works
lokalise-mcp --version  # (will start MCP server)

# Test with uvx
uvx --from ./dist/lokalise_mcp-0.1.0-py3-none-any.whl lokalise-mcp
```

### 2. Publish to Test PyPI

```bash
# Build fresh package
rm -rf dist/
uv build

# Publish to Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/

# Test installation from Test PyPI
uvx --index-url https://test.pypi.org/simple/ --from lokalise-mcp lokalise-mcp
```

### 3. Publish to Production PyPI

Once tested on Test PyPI:

```bash
# Make sure you have the latest build
uv build

# Publish to production PyPI
uv publish

# Test installation
uvx lokalise-mcp
```

### 4. Verify Installation

```bash
# Test with pip
pip install lokalise-mcp
lokalise-mcp  # Should start the MCP server

# Test with uvx (recommended)
uvx lokalise-mcp  # Should download and run latest version
```

## Updating Versions

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

2. Commit the version bump:
   ```bash
   git add pyproject.toml
   git commit -m "chore: bump version to 0.2.0"
   git tag v0.2.0
   git push && git push --tags
   ```

3. Build and publish:
   ```bash
   uv build
   uv publish
   ```

## Version Naming

Follow semantic versioning (semver):
- **0.1.0** - Initial release
- **0.1.1** - Bug fixes
- **0.2.0** - New features (backward compatible)
- **1.0.0** - Stable API, production ready
- **2.0.0** - Breaking changes

## Troubleshooting

### Authentication Failed

```bash
# Make sure token is set correctly
echo $UV_PUBLISH_TOKEN

# Or use --token flag
uv publish --token your-token-here
```

### Package Already Exists

You cannot overwrite existing versions on PyPI. Bump the version number in `pyproject.toml` first.

### Missing Files in Package

Check what's included:
```bash
tar -tzf dist/lokalise_mcp-0.1.0.tar.gz
```

Add files to pyproject.toml if needed.

## Continuous Integration (Future)

Consider setting up GitHub Actions to automatically publish when you push a tag:

```yaml
name: Publish to PyPI
on:
  push:
    tags:
      - 'v*'
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv build
      - run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```
