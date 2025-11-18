# GitHub Actions Secrets Setup

To enable automated publishing to PyPI and Docker Hub, you need to configure the following secrets in your GitHub repository.

## Required Secrets

### 1. PYPI_API_TOKEN

Your PyPI API token for publishing packages.

**How to get it:**
1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. Name: `github-actions-lokalise-mcp`
5. Scope: "Entire account" (or specific to `lokalise-mcp` project)
6. Copy the token (starts with `pypi-`)

**Add to GitHub:**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Paste your PyPI token
5. Click "Add secret"

### 2. DOCKER_USERNAME

Your Docker Hub username.

**Value:** `sidzan`

**Add to GitHub:**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `DOCKER_USERNAME`
4. Value: `sidzan`
5. Click "Add secret"

### 3. DOCKER_TOKEN

Your Docker Hub personal access token.

**How to get it:**
1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Description: `github-actions-lokalise-mcp`
4. Access permissions: "Read, Write, Delete"
5. Generate and copy the token (starts with `dckr_pat_`)

**Add to GitHub:**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `DOCKER_TOKEN`
4. Value: Paste your Docker Hub token
5. Click "Add secret"

## How the Workflow Works

Once secrets are configured, the workflow will automatically run when you push a version tag:

```bash
# Example: Release version 0.2.0
git tag v0.2.0
git push origin v0.2.0
```

This will:
1. Build the Python package
2. Publish to PyPI as `lokalise-mcp==0.2.0`
3. Build Docker image for multiple platforms (amd64, arm64)
4. Push to Docker Hub as:
   - `sidzan/lokalise-mcp:0.2.0`
   - `sidzan/lokalise-mcp:latest`

## Manual Trigger

You can also manually trigger the workflow from GitHub Actions tab without creating a tag.

## Verify Setup

After adding secrets, you can verify they're set correctly:
1. Go to Settings → Secrets and variables → Actions
2. You should see:
   - ✓ PYPI_API_TOKEN
   - ✓ DOCKER_USERNAME
   - ✓ DOCKER_TOKEN

All three should show "Updated X ago"
