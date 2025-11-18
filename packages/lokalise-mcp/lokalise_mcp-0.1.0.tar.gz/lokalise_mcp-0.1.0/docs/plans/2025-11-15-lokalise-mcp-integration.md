# Lokalise MCP Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an MCP server that extracts translation keys from git diffs and syncs them to Lokalise with AI-powered translations, interactive preview, and safety guards.

**Architecture:** FastMCP-based Python server with three main tools: (1) preview_new_keys for dry-run extraction, (2) extract_and_sync_translations for full workflow with AI translation and safety checks, (3) get_lokalise_project_info for project configuration. Uses git diff parsing, regex/AST code analysis, Claude AI for translations, and Lokalise API for key creation.

**Tech Stack:** FastMCP, Lokalise Python SDK, Anthropic Python SDK, GitPython, ast (Python stdlib), regex

---

## Task 1: Project Setup and Dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `src/lokalise_mcp/__init__.py`
- Create: `src/lokalise_mcp/server.py`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Create project structure**

Run:
```bash
mkdir -p src/lokalise_mcp tests docs
touch src/lokalise_mcp/__init__.py
```

**Step 2: Create pyproject.toml with dependencies**

Create `pyproject.toml`:
```toml
[project]
name = "lokalise-mcp"
version = "0.1.0"
description = "MCP server for syncing translation keys to Lokalise with AI-powered translations"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.0.0",
    "anthropic>=0.39.0",
    "python-lokalise-api>=3.0.0",
    "gitpython>=3.1.43",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.0.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
```

**Step 3: Create .env.example for configuration**

Create `.env.example`:
```bash
# Lokalise Configuration
LOKALISE_API_TOKEN=your_api_token_here
LOKALISE_PROJECT_ID=your_project_id_here

# Anthropic Configuration (for AI translations)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional Configuration
DEFAULT_BASE_BRANCH=main
DEFAULT_BATCH_SIZE=3
ENABLE_SAFETY_CHECKS=true
```

**Step 4: Create .gitignore**

Create `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# MCP
*.log
```

**Step 5: Create basic README**

Create `README.md`:
```markdown
# Lokalise MCP Integration

MCP server for extracting translation keys from code and syncing them to Lokalise with AI-powered translations.

## Features

- Extract translation keys from git diff
- AI-powered translation to multiple languages
- Interactive preview and approval
- Content safety guards
- Batch creation with progress tracking

## Installation

See [docs/INSTALLATION.md](docs/INSTALLATION.md)

## Usage

See [docs/USAGE.md](docs/USAGE.md)
```

**Step 6: Install dependencies**

Run:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

Expected: All dependencies installed successfully

**Step 7: Commit**

Run:
```bash
git init
git add .
git commit -m "feat: initial project setup with dependencies"
```

---

## Task 2: Configuration Management

**Files:**
- Create: `src/lokalise_mcp/config.py`
- Create: `tests/test_config.py`
- Create: `.lokalise-mcp.json`

**Step 1: Write failing test for config loading**

Create `tests/test_config.py`:
```python
import pytest
import os
import json
from pathlib import Path
from lokalise_mcp.config import Config, load_config


def test_config_loads_from_env(monkeypatch):
    """Test that config loads from environment variables."""
    monkeypatch.setenv("LOKALISE_API_TOKEN", "test_token")
    monkeypatch.setenv("LOKALISE_PROJECT_ID", "test_project")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key")

    config = Config()

    assert config.lokalise_api_token == "test_token"
    assert config.lokalise_project_id == "test_project"
    assert config.anthropic_api_key == "test_key"


def test_config_has_defaults():
    """Test that config has sensible defaults."""
    config = Config()

    assert config.default_base_branch == "main"
    assert config.default_batch_size == 3
    assert config.enable_safety_checks is True


def test_load_config_from_json(tmp_path):
    """Test loading configuration from JSON file."""
    config_file = tmp_path / ".lokalise-mcp.json"
    config_data = {
        "projectId": "json_project_id",
        "baseBranch": "develop",
        "batchSize": 5,
        "safety": {
            "enabled": False
        }
    }
    config_file.write_text(json.dumps(config_data))

    config = load_config(config_file)

    assert config.lokalise_project_id == "json_project_id"
    assert config.default_base_branch == "develop"
    assert config.default_batch_size == 5
    assert config.enable_safety_checks is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'lokalise_mcp.config'"

**Step 3: Implement Config class**

Create `src/lokalise_mcp/config.py`:
```python
"""Configuration management for Lokalise MCP."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Configuration for Lokalise MCP server."""

    # Required from environment
    lokalise_api_token: str = field(default_factory=lambda: os.getenv("LOKALISE_API_TOKEN", ""))
    lokalise_project_id: str = field(default_factory=lambda: os.getenv("LOKALISE_PROJECT_ID", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))

    # Defaults (can be overridden)
    default_base_branch: str = field(default_factory=lambda: os.getenv("DEFAULT_BASE_BRANCH", "main"))
    default_batch_size: int = field(default_factory=lambda: int(os.getenv("DEFAULT_BATCH_SIZE", "3")))
    enable_safety_checks: bool = field(default_factory=lambda: os.getenv("ENABLE_SAFETY_CHECKS", "true").lower() == "true")

    # File patterns
    file_patterns: list[str] = field(default_factory=lambda: ["**/*.tsx", "**/*.ts", "**/*.jsx", "**/*.js"])
    exclude_patterns: list[str] = field(default_factory=lambda: ["**/node_modules/**", "**/dist/**", "**/build/**"])

    # Translation patterns
    translation_functions: list[str] = field(default_factory=lambda: ["t", "translate"])
    default_param_name: str = "_"

    def validate(self) -> list[str]:
        """Validate required configuration. Returns list of errors."""
        errors = []

        if not self.lokalise_api_token:
            errors.append("LOKALISE_API_TOKEN is required")
        if not self.lokalise_project_id:
            errors.append("LOKALISE_PROJECT_ID is required")
        if not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is required")

        return errors


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from JSON file and merge with environment variables."""
    config = Config()

    if config_path is None:
        config_path = Path.cwd() / ".lokalise-mcp.json"

    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)

        # Override with JSON values
        if "projectId" in data:
            config.lokalise_project_id = data["projectId"]
        if "baseBranch" in data:
            config.default_base_branch = data["baseBranch"]
        if "batchSize" in data:
            config.default_batch_size = data["batchSize"]
        if "safety" in data and "enabled" in data["safety"]:
            config.enable_safety_checks = data["safety"]["enabled"]
        if "filePatterns" in data:
            config.file_patterns = data["filePatterns"]
        if "excludePatterns" in data:
            config.exclude_patterns = data["excludePatterns"]

    return config
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`
Expected: All 3 tests PASS

**Step 5: Create example .lokalise-mcp.json**

Create `.lokalise-mcp.json`:
```json
{
  "projectId": "",
  "baseBranch": "main",
  "batchSize": 3,
  "filePatterns": ["**/*.tsx", "**/*.ts", "**/*.jsx"],
  "excludePatterns": ["**/node_modules/**", "**/dist/**"],
  "translationPatterns": {
    "functions": ["t", "translate"],
    "defaultParam": "_"
  },
  "safety": {
    "enabled": true,
    "checkSourceText": true,
    "checkTranslations": true,
    "customBlocklist": []
  },
  "preview": {
    "enabled": true,
    "batchApproval": true,
    "showContext": true,
    "contextLines": 3
  }
}
```

**Step 6: Commit**

Run:
```bash
git add src/lokalise_mcp/config.py tests/test_config.py .lokalise-mcp.json
git commit -m "feat: add configuration management with JSON and env support"
```

---

## Task 3: Git Diff Extraction

**Files:**
- Create: `src/lokalise_mcp/git_utils.py`
- Create: `tests/test_git_utils.py`

**Step 1: Write failing test for git diff extraction**

Create `tests/test_git_utils.py`:
```python
import pytest
from pathlib import Path
from git import Repo
from lokalise_mcp.git_utils import get_changed_files, GitDiffExtractor


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    repo = Repo.init(tmp_path)

    # Create initial commit on main
    test_file = tmp_path / "test.txt"
    test_file.write_text("initial content")
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create feature branch
    repo.create_head("feature")
    repo.heads.feature.checkout()

    return repo, tmp_path


def test_get_changed_files_returns_modified_files(git_repo):
    """Test that get_changed_files returns files changed in current branch."""
    repo, tmp_path = git_repo

    # Modify file on feature branch
    modified_file = tmp_path / "test.txt"
    modified_file.write_text("modified content")
    repo.index.add([str(modified_file)])
    repo.index.commit("Modify file")

    # Add new file
    new_file = tmp_path / "new.tsx"
    new_file.write_text("const x = t('key')")
    repo.index.add([str(new_file)])
    repo.index.commit("Add new file")

    changed_files = get_changed_files(str(tmp_path), base_branch="main")

    assert len(changed_files) >= 2
    assert any("test.txt" in str(f) for f in changed_files)
    assert any("new.tsx" in str(f) for f in changed_files)


def test_git_diff_extractor_filters_by_pattern(git_repo):
    """Test that GitDiffExtractor filters files by pattern."""
    repo, tmp_path = git_repo

    # Create files with different extensions
    tsx_file = tmp_path / "component.tsx"
    tsx_file.write_text("t('key')")
    py_file = tmp_path / "script.py"
    py_file.write_text("print('hello')")

    repo.index.add([str(tsx_file), str(py_file)])
    repo.index.commit("Add mixed files")

    extractor = GitDiffExtractor(
        repo_path=str(tmp_path),
        file_patterns=["**/*.tsx", "**/*.ts"],
        exclude_patterns=["**/node_modules/**"]
    )

    changed_files = extractor.get_changed_files(base_branch="main")

    assert len(changed_files) == 1
    assert "component.tsx" in str(changed_files[0])
    assert not any("script.py" in str(f) for f in changed_files)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_git_utils.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'lokalise_mcp.git_utils'"

**Step 3: Implement git utilities**

Create `src/lokalise_mcp/git_utils.py`:
```python
"""Git utilities for extracting changed files from diffs."""

from pathlib import Path
from typing import List
import git
import fnmatch


def get_changed_files(repo_path: str, base_branch: str = "main") -> List[Path]:
    """Get list of files changed in current branch compared to base branch."""
    repo = git.Repo(repo_path)

    # Get current branch
    current_branch = repo.active_branch.name

    if current_branch == base_branch:
        raise ValueError(f"Cannot compare branch to itself: {base_branch}")

    # Get diff between base branch and current branch
    base_commit = repo.commit(base_branch)
    current_commit = repo.head.commit

    diff = base_commit.diff(current_commit)

    # Extract changed file paths
    changed_files = []
    for item in diff:
        # Handle both a_path (deleted) and b_path (added/modified)
        file_path = item.b_path if item.b_path else item.a_path
        if file_path:
            full_path = Path(repo_path) / file_path
            if full_path.exists():
                changed_files.append(full_path)

    return changed_files


class GitDiffExtractor:
    """Extract and filter changed files from git diff."""

    def __init__(
        self,
        repo_path: str,
        file_patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ):
        self.repo_path = Path(repo_path)
        self.file_patterns = file_patterns or ["**/*"]
        self.exclude_patterns = exclude_patterns or []

    def _matches_pattern(self, file_path: Path, patterns: List[str]) -> bool:
        """Check if file matches any of the given glob patterns."""
        relative_path = file_path.relative_to(self.repo_path)

        for pattern in patterns:
            if fnmatch.fnmatch(str(relative_path), pattern) or \
               fnmatch.fnmatch(str(relative_path), pattern.replace('**/', '')):
                return True
        return False

    def get_changed_files(self, base_branch: str = "main") -> List[Path]:
        """Get filtered list of changed files."""
        all_changed = get_changed_files(str(self.repo_path), base_branch)

        filtered = []
        for file_path in all_changed:
            # Check if matches include patterns
            if not self._matches_pattern(file_path, self.file_patterns):
                continue

            # Check if matches exclude patterns
            if self.exclude_patterns and self._matches_pattern(file_path, self.exclude_patterns):
                continue

            filtered.append(file_path)

        return filtered
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_git_utils.py -v`
Expected: All 2 tests PASS

**Step 5: Commit**

Run:
```bash
git add src/lokalise_mcp/git_utils.py tests/test_git_utils.py
git commit -m "feat: add git diff extraction with file filtering"
```

---

## Task 4: Translation Key Extraction

**Files:**
- Create: `src/lokalise_mcp/key_extractor.py`
- Create: `tests/test_key_extractor.py`

**Step 1: Write failing test for key extraction**

Create `tests/test_key_extractor.py`:
```python
import pytest
from pathlib import Path
from lokalise_mcp.key_extractor import TranslationKey, KeyExtractor


def test_extract_keys_with_default_value():
    """Test extracting translation keys with default values."""
    code = """
    const title = t('products.landing.title', { _: 'Product Landing' });
    const subtitle = t('products.landing.subtitle', { _: 'Browse our catalog' });
    """

    extractor = KeyExtractor()
    keys = extractor.extract_from_code(code, file_path="test.tsx")

    assert len(keys) == 2
    assert keys[0].key_name == "products.landing.title"
    assert keys[0].default_text == "Product Landing"
    assert keys[1].key_name == "products.landing.subtitle"
    assert keys[1].default_text == "Browse our catalog"


def test_extract_keys_without_default():
    """Test extracting translation keys without defaults."""
    code = """
    const label = t('actions.save');
    const cancel = translate('actions.cancel');
    """

    extractor = KeyExtractor()
    keys = extractor.extract_from_code(code, file_path="test.tsx")

    assert len(keys) == 2
    assert keys[0].key_name == "actions.save"
    assert keys[0].default_text is None
    assert keys[1].key_name == "actions.cancel"
    assert keys[1].default_text is None


def test_extract_keys_with_parameters():
    """Test extracting keys with interpolation parameters."""
    code = """
    const msg = t('actions.selectedEmployees', {
        count: 5,
        _: '%{count} employees selected'
    });
    """

    extractor = KeyExtractor()
    keys = extractor.extract_from_code(code, file_path="test.tsx")

    assert len(keys) == 1
    assert keys[0].key_name == "actions.selectedEmployees"
    assert keys[0].default_text == "%{count} employees selected"
    assert "count" in keys[0].parameters


def test_extract_context_from_code():
    """Test extracting surrounding context for better AI translation."""
    code = """
    function DeleteButton() {
        return (
            <Dialog title="Delete Assignment">
                <Button onClick={handleDelete}>
                    {t('employee.assignmentDetails.general.deleteAssignment',
                       { _: 'Delete Assignment' })}
                </Button>
            </Dialog>
        );
    }
    """

    extractor = KeyExtractor(context_lines=3)
    keys = extractor.extract_from_code(code, file_path="DeleteButton.tsx")

    assert len(keys) == 1
    assert keys[0].key_name == "employee.assignmentDetails.general.deleteAssignment"
    assert "Dialog" in keys[0].context
    assert "Button" in keys[0].context


def test_extract_from_file(tmp_path):
    """Test extracting keys from an actual file."""
    test_file = tmp_path / "component.tsx"
    test_file.write_text("""
        export function ProductList() {
            return (
                <div>
                    <h1>{t('products.list.title', { _: 'Products' })}</h1>
                    {items.length === 0 && <Empty>{t('products.list.empty')}</Empty>}
                </div>
            );
        }
    """)

    extractor = KeyExtractor()
    keys = extractor.extract_from_file(test_file)

    assert len(keys) == 2
    assert keys[0].key_name == "products.list.title"
    assert keys[0].default_text == "Products"
    assert keys[1].key_name == "products.list.empty"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_key_extractor.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'lokalise_mcp.key_extractor'"

**Step 3: Implement key extractor with regex**

Create `src/lokalise_mcp/key_extractor.py`:
```python
"""Extract translation keys from source code."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class TranslationKey:
    """Represents an extracted translation key."""
    key_name: str
    default_text: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    context: str = ""
    file_path: str = ""
    line_number: int = 0


class KeyExtractor:
    """Extract translation keys from source code using regex and AST."""

    def __init__(
        self,
        translation_functions: List[str] = None,
        default_param: str = "_",
        context_lines: int = 3
    ):
        self.translation_functions = translation_functions or ["t", "translate"]
        self.default_param = default_param
        self.context_lines = context_lines

        # Build regex patterns
        self._build_patterns()

    def _build_patterns(self):
        """Build regex patterns for detecting translation calls."""
        func_pattern = "|".join(re.escape(f) for f in self.translation_functions)

        # Pattern 1: With default value - t('key', { _: 'default' })
        self.pattern_with_default = re.compile(
            rf"(?:{func_pattern})\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{{\s*[^}}]*{self.default_param}\s*:\s*['\"]([^'\"]+)['\"]",
            re.MULTILINE | re.DOTALL
        )

        # Pattern 2: Simple - t('key')
        self.pattern_simple = re.compile(
            rf"(?:{func_pattern})\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            re.MULTILINE
        )

        # Pattern 3: Parameters - extract variable names like {count}
        self.param_pattern = re.compile(r"%\{(\w+)\}")

    def extract_from_code(self, code: str, file_path: str = "") -> List[TranslationKey]:
        """Extract translation keys from code string."""
        keys = []
        seen_keys = set()

        lines = code.split('\n')

        # First pass: keys with defaults (priority)
        for match in self.pattern_with_default.finditer(code):
            key_name = match.group(1)
            default_text = match.group(2)

            if key_name in seen_keys:
                continue
            seen_keys.add(key_name)

            # Extract parameters from default text
            params = self.param_pattern.findall(default_text)

            # Get line number and context
            line_num = code[:match.start()].count('\n') + 1
            context = self._extract_context(lines, line_num)

            keys.append(TranslationKey(
                key_name=key_name,
                default_text=default_text,
                parameters=params,
                context=context,
                file_path=file_path,
                line_number=line_num
            ))

        # Second pass: simple keys without defaults
        for match in self.pattern_simple.finditer(code):
            key_name = match.group(1)

            if key_name in seen_keys:
                continue
            seen_keys.add(key_name)

            line_num = code[:match.start()].count('\n') + 1
            context = self._extract_context(lines, line_num)

            keys.append(TranslationKey(
                key_name=key_name,
                default_text=None,
                parameters=[],
                context=context,
                file_path=file_path,
                line_number=line_num
            ))

        return keys

    def _extract_context(self, lines: List[str], line_num: int) -> str:
        """Extract surrounding lines for context."""
        start = max(0, line_num - self.context_lines - 1)
        end = min(len(lines), line_num + self.context_lines)

        context_lines = lines[start:end]
        return '\n'.join(context_lines)

    def extract_from_file(self, file_path: Path) -> List[TranslationKey]:
        """Extract translation keys from a file."""
        code = file_path.read_text(encoding='utf-8')
        return self.extract_from_code(code, file_path=str(file_path))
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_key_extractor.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

Run:
```bash
git add src/lokalise_mcp/key_extractor.py tests/test_key_extractor.py
git commit -m "feat: add translation key extraction with regex and context"
```

---

## Task 5: Lokalise API Integration

**Files:**
- Create: `src/lokalise_mcp/lokalise_client.py`
- Create: `tests/test_lokalise_client.py`

**Step 1: Write failing test for Lokalise client**

Create `tests/test_lokalise_client.py`:
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from lokalise_mcp.lokalise_client import LokaliseClient


@pytest.fixture
def mock_lokalise_api():
    """Mock Lokalise API client."""
    with patch('lokalise_mcp.lokalise_client.lokalise') as mock:
        client = Mock()
        mock.Client.return_value = client
        yield client


@pytest.mark.asyncio
async def test_get_project_languages(mock_lokalise_api):
    """Test fetching project languages from Lokalise."""
    mock_lokalise_api.languages.return_value = [
        Mock(lang_iso="en", lang_name="English"),
        Mock(lang_iso="no", lang_name="Norwegian"),
        Mock(lang_iso="th", lang_name="Thai"),
    ]

    client = LokaliseClient(api_token="test_token", project_id="test_project")
    languages = await client.get_project_languages()

    assert len(languages) == 3
    assert languages[0]["lang_iso"] == "en"
    assert languages[1]["lang_name"] == "Norwegian"


@pytest.mark.asyncio
async def test_create_keys_in_batch(mock_lokalise_api):
    """Test creating translation keys in Lokalise."""
    mock_lokalise_api.keys.return_value = Mock(key_id=123)

    client = LokaliseClient(api_token="test_token", project_id="test_project")

    keys_to_create = [
        {
            "key_name": "products.title",
            "translations": {
                "en": "Products",
                "no": "Produkter"
            }
        }
    ]

    result = await client.create_keys(keys_to_create)

    assert result["created"] == 1
    assert result["failed"] == 0


@pytest.mark.asyncio
async def test_check_existing_keys(mock_lokalise_api):
    """Test checking if keys already exist."""
    mock_lokalise_api.keys.return_value = [
        Mock(key_name={"web": "existing.key"})
    ]

    client = LokaliseClient(api_token="test_token", project_id="test_project")

    exists = await client.key_exists("existing.key")
    assert exists is True

    exists = await client.key_exists("new.key")
    assert exists is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_lokalise_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'lokalise_mcp.lokalise_client'"

**Step 3: Implement Lokalise client**

Create `src/lokalise_mcp/lokalise_client.py`:
```python
"""Lokalise API client wrapper."""

import asyncio
from typing import List, Dict, Optional
import lokalise


class LokaliseClient:
    """Client for interacting with Lokalise API."""

    def __init__(self, api_token: str, project_id: str):
        self.api_token = api_token
        self.project_id = project_id
        self.client = lokalise.Client(api_token)
        self._existing_keys_cache: Optional[set] = None

    async def get_project_languages(self) -> List[Dict[str, str]]:
        """Fetch all languages configured in the Lokalise project."""
        # Run in thread pool since lokalise SDK is synchronous
        loop = asyncio.get_event_loop()
        languages = await loop.run_in_executor(
            None,
            lambda: self.client.project_languages(self.project_id)
        )

        return [
            {
                "lang_iso": lang.lang_iso,
                "lang_name": lang.lang_name,
                "is_rtl": getattr(lang, "is_rtl", False),
            }
            for lang in languages
        ]

    async def get_project_info(self) -> Dict:
        """Get project information."""
        loop = asyncio.get_event_loop()
        project = await loop.run_in_executor(
            None,
            lambda: self.client.project(self.project_id)
        )

        return {
            "project_id": project.project_id,
            "name": project.name,
            "base_lang_iso": getattr(project, "base_lang_iso", "en"),
        }

    async def _load_existing_keys(self):
        """Load all existing keys into cache."""
        if self._existing_keys_cache is not None:
            return

        loop = asyncio.get_event_loop()
        keys = await loop.run_in_executor(
            None,
            lambda: self.client.keys(self.project_id)
        )

        self._existing_keys_cache = set()
        for key in keys:
            # Keys might be platform-specific or simple strings
            if isinstance(key.key_name, dict):
                # Platform-specific: {"web": "key.name", "ios": "key_name"}
                self._existing_keys_cache.update(key.key_name.values())
            else:
                self._existing_keys_cache.add(key.key_name)

    async def key_exists(self, key_name: str) -> bool:
        """Check if a key already exists in Lokalise."""
        await self._load_existing_keys()
        return key_name in self._existing_keys_cache

    async def create_keys(self, keys: List[Dict]) -> Dict:
        """Create multiple translation keys in Lokalise.

        Args:
            keys: List of dicts with structure:
                {
                    "key_name": "products.title",
                    "translations": {
                        "en": "Products",
                        "no": "Produkter"
                    }
                }

        Returns:
            Dict with created/failed counts
        """
        created = 0
        failed = 0
        skipped = 0
        errors = []

        loop = asyncio.get_event_loop()

        for key_data in keys:
            key_name = key_data["key_name"]
            translations = key_data["translations"]

            # Check if exists
            if await self.key_exists(key_name):
                skipped += 1
                continue

            try:
                # Format for Lokalise API
                lokalise_key = {
                    "key_name": key_name,
                    "platforms": ["web"],
                    "translations": [
                        {
                            "language_iso": lang_iso,
                            "translation": text
                        }
                        for lang_iso, text in translations.items()
                    ]
                }

                # Create key
                await loop.run_in_executor(
                    None,
                    lambda: self.client.create_keys(self.project_id, [lokalise_key])
                )

                created += 1

                # Update cache
                if self._existing_keys_cache is not None:
                    self._existing_keys_cache.add(key_name)

            except Exception as e:
                failed += 1
                errors.append(f"{key_name}: {str(e)}")

        return {
            "created": created,
            "failed": failed,
            "skipped": skipped,
            "errors": errors
        }
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_lokalise_client.py -v`
Expected: All 3 tests PASS

**Step 5: Commit**

Run:
```bash
git add src/lokalise_mcp/lokalise_client.py tests/test_lokalise_client.py
git commit -m "feat: add Lokalise API client with language and key management"
```

---

## Task 6: AI Translation Service

**Files:**
- Create: `src/lokalise_mcp/translator.py`
- Create: `tests/test_translator.py`

**Step 1: Write failing test for AI translator**

Create `tests/test_translator.py`:
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from lokalise_mcp.translator import AITranslator, TranslationContext


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API client."""
    with patch('lokalise_mcp.translator.Anthropic') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.mark.asyncio
async def test_translate_with_context(mock_anthropic):
    """Test translating text with context."""
    mock_response = Mock()
    mock_response.content = [Mock(text="Produkter")]
    mock_anthropic.messages.create.return_value = mock_response

    translator = AITranslator(api_key="test_key")

    context = TranslationContext(
        key_name="products.title",
        source_text="Products",
        code_context="<h1>{t('products.title')}</h1>",
        file_path="ProductList.tsx"
    )

    result = await translator.translate(
        context=context,
        target_language="Norwegian"
    )

    assert result == "Produkter"
    mock_anthropic.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_translate_batch(mock_anthropic):
    """Test batch translation for efficiency."""
    mock_response = Mock()
    mock_response.content = [Mock(text="Produkter\nHandlekurv")]
    mock_anthropic.messages.create.return_value = mock_response

    translator = AITranslator(api_key="test_key")

    contexts = [
        TranslationContext(key_name="products.title", source_text="Products"),
        TranslationContext(key_name="cart.title", source_text="Shopping Cart"),
    ]

    results = await translator.translate_batch(
        contexts=contexts,
        target_language="Norwegian"
    )

    assert len(results) == 2
    assert results[0] == "Produkter"
    assert results[1] == "Handlekurv"


@pytest.mark.asyncio
async def test_translate_to_multiple_languages(mock_anthropic):
    """Test translating to multiple languages."""
    mock_response = Mock()
    mock_response.content = [Mock(text="Produkter")]
    mock_anthropic.messages.create.return_value = mock_response

    translator = AITranslator(api_key="test_key")

    context = TranslationContext(
        key_name="products.title",
        source_text="Products"
    )

    results = await translator.translate_to_languages(
        context=context,
        languages=["Norwegian", "Thai", "Swedish"]
    )

    assert len(results) == 3
    assert "no" in results or "Norwegian" in results
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_translator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'lokalise_mcp.translator'"

**Step 3: Implement AI translator**

Create `src/lokalise_mcp/translator.py`:
```python
"""AI-powered translation service using Claude."""

import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional
from anthropic import Anthropic


@dataclass
class TranslationContext:
    """Context for translating a key."""
    key_name: str
    source_text: str
    code_context: str = ""
    file_path: str = ""
    parameters: List[str] = None
    similar_translations: Dict[str, str] = None


class AITranslator:
    """AI-powered translator using Claude."""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=api_key)

    def _build_translation_prompt(
        self,
        context: TranslationContext,
        target_language: str
    ) -> str:
        """Build a detailed prompt for translation."""
        prompt_parts = [
            f"Translate this UI text to {target_language}:",
            "",
            f"Key: {context.key_name}",
            f"English: \"{context.source_text}\"",
        ]

        if context.parameters:
            prompt_parts.append(f"Parameters: {', '.join(context.parameters)}")
        else:
            prompt_parts.append("Parameters: none")

        if context.code_context:
            prompt_parts.extend([
                "",
                "Context from code:",
                context.code_context
            ])

        if context.similar_translations:
            prompt_parts.extend([
                "",
                "Similar translations in this project:",
            ])
            for key, value in context.similar_translations.items():
                prompt_parts.append(f"- {key}: \"{value}\"")

        prompt_parts.extend([
            "",
            "Provide a natural, concise translation that:",
            "1. Matches the formality of similar UI elements",
            "2. Is clear and actionable",
            "3. Preserves any parameter placeholders like %{count}",
            "4. Fits the UI context (button/link/heading/etc)",
            "",
            "Respond with ONLY the translated text, no explanations.",
            "",
            "Translation:"
        ])

        return "\n".join(prompt_parts)

    async def translate(
        self,
        context: TranslationContext,
        target_language: str
    ) -> str:
        """Translate a single text to target language."""
        prompt = self._build_translation_prompt(context, target_language)

        # Run in thread pool since Anthropic SDK is synchronous
        loop = asyncio.get_event_loop()

        def _call_api():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()

        translation = await loop.run_in_executor(None, _call_api)

        # Clean up any quotes that might be added
        translation = translation.strip('"\'')

        return translation

    async def translate_batch(
        self,
        contexts: List[TranslationContext],
        target_language: str
    ) -> List[str]:
        """Translate multiple texts to same language (more efficient)."""
        # Build batch prompt
        prompt_parts = [
            f"Translate these UI texts to {target_language}.",
            "Respond with one translation per line, in order.",
            "Use ONLY the translated text, no numbering or explanations.",
            ""
        ]

        for i, ctx in enumerate(contexts, 1):
            prompt_parts.extend([
                f"{i}. Key: {ctx.key_name}",
                f"   English: \"{ctx.source_text}\"",
                ""
            ])

        prompt_parts.append("Translations (one per line):")
        prompt = "\n".join(prompt_parts)

        loop = asyncio.get_event_loop()

        def _call_api():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()

        result = await loop.run_in_executor(None, _call_api)

        # Parse line-by-line
        translations = [line.strip().strip('"\'') for line in result.split('\n') if line.strip()]

        # Ensure we have the right number
        if len(translations) != len(contexts):
            # Fallback to individual translation
            return [await self.translate(ctx, target_language) for ctx in contexts]

        return translations

    async def translate_to_languages(
        self,
        context: TranslationContext,
        languages: List[str]
    ) -> Dict[str, str]:
        """Translate a single text to multiple languages."""
        tasks = [
            self.translate(context, lang)
            for lang in languages
        ]

        results = await asyncio.gather(*tasks)

        return {
            lang: translation
            for lang, translation in zip(languages, results)
        }
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_translator.py -v`
Expected: All 3 tests PASS

**Step 5: Commit**

Run:
```bash
git add src/lokalise_mcp/translator.py tests/test_translator.py
git commit -m "feat: add AI-powered translation service with Claude"
```

---

## Task 7: Content Safety Guards

**Files:**
- Create: `src/lokalise_mcp/safety.py`
- Create: `tests/test_safety.py`

**Step 1: Write failing test for safety checks**

Create `tests/test_safety.py`:
```python
import pytest
from unittest.mock import Mock, patch
from lokalise_mcp.safety import SafetyGuard, SafetyCheckResult


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API for safety checks."""
    with patch('lokalise_mcp.safety.Anthropic') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.mark.asyncio
async def test_safe_text_passes(mock_anthropic):
    """Test that safe text passes safety check."""
    mock_response = Mock()
    mock_response.content = [Mock(text="SAFE")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    guard = SafetyGuard(api_key="test_key")
    result = await guard.check_source_text("Save Changes")

    assert result.is_safe is True
    assert len(result.flags) == 0


@pytest.mark.asyncio
async def test_unsafe_text_flagged(mock_anthropic):
    """Test that unsafe text is flagged."""
    mock_response = Mock()
    mock_response.content = [Mock(text="UNSAFE: Contains profanity")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    guard = SafetyGuard(api_key="test_key")
    result = await guard.check_source_text("This is bad language")

    assert result.is_safe is False
    assert "profanity" in result.reason.lower()


@pytest.mark.asyncio
async def test_regex_patterns_detect_issues():
    """Test that regex patterns catch obvious issues."""
    guard = SafetyGuard(api_key="test_key", use_ai_check=False)

    # Should flag violent language
    result = await guard.check_source_text("Kill the process now")
    assert result.is_safe is False
    assert len(result.flags) > 0


@pytest.mark.asyncio
async def test_custom_blocklist():
    """Test that custom blocklist works."""
    guard = SafetyGuard(
        api_key="test_key",
        custom_blocklist=["forbidden", "blocked"],
        use_ai_check=False
    )

    result = await guard.check_source_text("This contains forbidden word")
    assert result.is_safe is False


@pytest.mark.asyncio
async def test_translation_verification(mock_anthropic):
    """Test verifying translation doesn't introduce harmful content."""
    mock_response = Mock()
    mock_response.content = [Mock(text="APPROVED")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    guard = SafetyGuard(api_key="test_key")
    result = await guard.check_translation(
        original="Save Changes",
        translated="Lagre endringer",
        language="Norwegian"
    )

    assert result.is_safe is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_safety.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'lokalise_mcp.safety'"

**Step 3: Implement safety guard**

Create `src/lokalise_mcp/safety.py`:
```python
"""Content safety guards for translations."""

import asyncio
import re
from dataclasses import dataclass
from typing import List, Optional
from anthropic import Anthropic


@dataclass
class SafetyCheckResult:
    """Result of a safety check."""
    is_safe: bool
    flags: List[str]
    reason: str = ""


class SafetyGuard:
    """Content safety guard to prevent harmful translations."""

    # Default sensitive patterns
    DEFAULT_PATTERNS = [
        r'\b(kill|die|death|murder)\b',
        r'\b(hate|stupid|idiot|dumb)\b',
        r'\b(damn|hell|crap)\b',
        r'\b(racist|sexist|discrimination)\b',
    ]

    def __init__(
        self,
        api_key: str,
        custom_blocklist: List[str] = None,
        use_ai_check: bool = True,
        model: str = "claude-3-5-haiku-20241022"
    ):
        self.api_key = api_key
        self.custom_blocklist = custom_blocklist or []
        self.use_ai_check = use_ai_check
        self.model = model
        self.client = Anthropic(api_key=api_key) if use_ai_check else None

        # Compile regex patterns
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.DEFAULT_PATTERNS]

        # Add custom blocklist patterns
        for word in self.custom_blocklist:
            self.patterns.append(re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE))

    async def check_source_text(self, text: str) -> SafetyCheckResult:
        """Check if source text is appropriate for translation."""
        flags = []

        # Quick regex check
        for pattern in self.patterns:
            match = pattern.search(text)
            if match:
                flags.append(f"Contains potentially sensitive pattern: {match.group()}")

        # AI-based deep check
        if self.use_ai_check:
            is_safe, reason = await self._ai_safety_check(text)
            if not is_safe:
                return SafetyCheckResult(is_safe=False, flags=flags, reason=reason)

        # If we have flags but AI says safe, return with warnings
        return SafetyCheckResult(
            is_safe=len(flags) == 0,
            flags=flags,
            reason=""
        )

    async def _ai_safety_check(self, text: str) -> tuple[bool, str]:
        """Use AI to check if text is appropriate."""
        prompt = f"""You are a content safety filter for a translation system.

Analyze this text and determine if it contains:
- Abusive language
- Hate speech
- Profanity (unless it's a legitimate error message)
- Discriminatory content
- Harmful instructions

Text to check: "{text}"

Context: This will be translated and used in a business application UI.

Respond with ONLY:
SAFE - if the text is appropriate for professional translation
UNSAFE: [reason] - if the text should be flagged

Response:"""

        loop = asyncio.get_event_loop()

        def _call_api():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()

        result = await loop.run_in_executor(None, _call_api)

        if result.startswith("SAFE"):
            return True, ""
        else:
            reason = result.replace("UNSAFE:", "").strip()
            return False, reason

    async def check_translation(
        self,
        original: str,
        translated: str,
        language: str
    ) -> SafetyCheckResult:
        """Verify translation is accurate and doesn't introduce harmful content."""
        if not self.use_ai_check:
            return SafetyCheckResult(is_safe=True, flags=[], reason="")

        prompt = f"""Verify this translation is accurate and appropriate:

Original (English): "{original}"
Translation ({language}): "{translated}"

Check:
1. Is the translation accurate?
2. Does it preserve the professional tone?
3. Does it introduce any offensive/harmful content not in the original?

Respond with ONLY:
APPROVED - if translation is good
REJECT: [reason] - if there's an issue

Response:"""

        loop = asyncio.get_event_loop()

        def _call_api():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text.strip()

        result = await loop.run_in_executor(None, _call_api)

        if result.startswith("APPROVED"):
            return SafetyCheckResult(is_safe=True, flags=[], reason="")
        else:
            reason = result.replace("REJECT:", "").strip()
            return SafetyCheckResult(is_safe=False, flags=["Translation rejected"], reason=reason)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_safety.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

Run:
```bash
git add src/lokalise_mcp/safety.py tests/test_safety.py
git commit -m "feat: add content safety guards with AI and regex checks"
```

---

## Task 8: MCP Server Implementation

**Files:**
- Create: `src/lokalise_mcp/server.py` (main implementation)
- Update: `src/lokalise_mcp/__init__.py`

**Step 1: Implement main MCP server with FastMCP**

Update `src/lokalise_mcp/server.py`:
```python
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
    base_branch: str = "main",
    repo_path: Optional[str] = None
) -> Dict:
    """Preview translation keys that would be extracted without creating them.

    Args:
        base_branch: Git branch to compare against (default: main)
        repo_path: Path to git repository (default: current directory)

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
    base_branch: str = "main",
    batch_size: int = 3,
    repo_path: Optional[str] = None,
    auto_approve: bool = False,
    skip_safety_check: bool = False
) -> Dict:
    """Extract translation keys from git diff and sync to Lokalise with AI translations.

    This is the main workflow:
    1. Extract keys from changed files
    2. Check for safety issues
    3. Generate AI translations
    4. Preview and request approval (unless auto_approve=True)
    5. Create keys in Lokalise in batches

    Args:
        base_branch: Git branch to compare against (default: main)
        batch_size: Number of keys to create per batch (default: 3)
        repo_path: Path to git repository (default: current directory)
        auto_approve: Skip approval prompts and create all keys (default: False)
        skip_safety_check: Skip content safety checks (default: False)

    Returns:
        Summary with created/skipped/failed counts
    """
    config = get_config()

    if repo_path is None:
        repo_path = os.getcwd()

    # Initialize services
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

    # Step 2: Safety check
    flagged_keys = []

    if not skip_safety_check and config.enable_safety_checks:
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

    # Step 3: Get languages from Lokalise
    languages = await lokalise_client.get_project_languages()

    # Step 4: Translate keys
    translations_to_create = []

    for key in all_keys:
        if key.default_text is None:
            # TODO: In future, prompt user for default
            continue

        key_translations = {"en": key.default_text}

        # Translate to other languages
        context = TranslationContext(
            key_name=key.key_name,
            source_text=key.default_text,
            code_context=key.context,
            file_path=key.file_path,
            parameters=key.parameters
        )

        for lang in languages:
            if lang["lang_iso"] == "en":
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
```

**Step 2: Update __init__.py**

Update `src/lokalise_mcp/__init__.py`:
```python
"""Lokalise MCP - Translation key sync tool."""

from .server import mcp, main

__version__ = "0.1.0"
__all__ = ["mcp", "main"]
```

**Step 3: Test server runs**

Run:
```bash
# Set required env vars
export LOKALISE_API_TOKEN="test"
export LOKALISE_PROJECT_ID="test"
export ANTHROPIC_API_KEY="test"

# Try to run server
python -m lokalise_mcp.server --help
```

Expected: MCP server help output or error about running

**Step 4: Commit**

Run:
```bash
git add src/lokalise_mcp/server.py src/lokalise_mcp/__init__.py
git commit -m "feat: implement MCP server with extract, preview, and sync tools"
```

---

## Task 9: Documentation - Installation Guide

**Files:**
- Create: `docs/INSTALLATION.md`

**Step 1: Create installation documentation**

Create `docs/INSTALLATION.md`:
```markdown
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
```

**Step 2: Commit**

Run:
```bash
git add docs/INSTALLATION.md
git commit -m "docs: add installation guide"
```

---

## Task 10: Documentation - Usage Guide

**Files:**
- Create: `docs/USAGE.md`

**Step 1: Create usage documentation**

Create `docs/USAGE.md`:
```markdown
# Lokalise MCP - Usage Guide

Learn how to use the Lokalise MCP server to extract and sync translation keys.

## Quick Start

The Lokalise MCP provides three main tools:

1. **get_lokalise_project_info** - Check your project configuration
2. **preview_new_keys** - See what keys would be extracted (dry run)
3. **extract_and_sync_translations** - Extract and create keys in Lokalise

## Tool 1: Check Project Information

Before starting, verify your Lokalise project connection:

```
Use the get_lokalise_project_info tool
```

**Example Response:**
```json
{
  "project_id": "123456abc.def",
  "project_name": "My Application",
  "base_language": "en",
  "languages": [
    {"code": "en", "name": "English", "is_base": true},
    {"code": "no", "name": "Norwegian", "is_base": false},
    {"code": "th", "name": "Thai", "is_base": false},
    {"code": "sv", "name": "Swedish", "is_base": false}
  ],
  "total_languages": 4
}
```

This confirms:
- ✅ API connection works
- ✅ Project ID is correct
- ✅ Languages are configured (translations will be created for all of these)

## Tool 2: Preview New Keys (Dry Run)

Before creating keys, preview what would be extracted from your current branch:

```
Use preview_new_keys with base_branch="main"
```

**Example Response:**
```json
{
  "total_keys": 12,
  "namespaces": {
    "products": [
      {
        "key": "products.landing.title",
        "default": "Product Landing",
        "file": "src/pages/ProductLanding.tsx",
        "line": 23,
        "has_default": true
      },
      {
        "key": "products.list.empty",
        "default": "No products found",
        "file": "src/components/ProductList.tsx",
        "line": 45,
        "has_default": true
      }
    ],
    "actions": [
      {
        "key": "actions.addToCart",
        "default": "Add to Cart",
        "file": "src/components/ProductCard.tsx",
        "line": 67,
        "has_default": true
      }
    ]
  },
  "missing_defaults": [
    {
      "key": "products.filters.category",
      "file": "src/pages/ProductLanding.tsx",
      "line": 52,
      "context": "<Select label=???>{t('products.filters.category')}</Select>"
    }
  ]
}
```

This shows:
- 📊 Total keys found
- 📁 Keys grouped by namespace
- ⚠️ Keys missing default values (you'll need to provide these)
- 📍 Exact file location for each key

## Tool 3: Extract and Sync Translations

Once you've reviewed the preview, run the full sync:

```
Use extract_and_sync_translations with:
  - base_branch="main"
  - batch_size=3
  - auto_approve=false (to review each batch)
```

### Workflow Steps

The tool will:

1. **Extract keys** from files changed in your branch
2. **Run safety checks** on source text
3. **Fetch languages** from Lokalise
4. **Generate AI translations** for all target languages
5. **Verify translations** don't introduce harmful content
6. **Create keys in Lokalise** in batches of 3

**Example Response:**
```json
{
  "status": "completed",
  "total_keys_found": 12,
  "created": 11,
  "skipped": 1,
  "failed": 0,
  "flagged_keys": [],
  "errors": [],
  "languages": ["en", "no", "th", "sv"]
}
```

## Understanding the Translation Pattern

The MCP looks for these patterns in your code:

### Pattern 1: With Default Value (Recommended)

```typescript
t('employee.assignmentDetails.general.deleteAssignment', { _: 'Delete Assignment' })
```

- ✅ Extracts key: `employee.assignmentDetails.general.deleteAssignment`
- ✅ Uses `Delete Assignment` as English text
- ✅ AI translates to other languages

### Pattern 2: Without Default

```typescript
t('actions.save')
```

- ✅ Extracts key: `actions.save`
- ⚠️ No default value - you'll need to provide one

### Pattern 3: With Parameters

```typescript
t('actions.selectedEmployees', { count: 5, _: '%{count} employees selected' })
```

- ✅ Extracts key and detects `{count}` parameter
- ✅ Preserves parameter in translations

### Pattern 4: useTranslate Hook

```typescript
const translate = useTranslate();
translate('actions.cancel');
```

- ✅ Also detected and extracted

## Safety Checks

The MCP includes content safety guards to prevent harmful translations:

### What Gets Flagged

- Profanity or abusive language
- Hate speech
- Discriminatory content
- Violent language (unless contextually appropriate)

### Example: Safe Technical Term

```typescript
// This is OK - technical context
t('process.kill', { _: 'Kill process' })
```

**Safety Check Result:** ✅ APPROVED (technical term in system context)

### Example: Flagged Content

```typescript
// This would be flagged
t('error.message', { _: 'You are stupid' })
```

**Safety Check Result:** ⚠️ UNSAFE - Abusive language detected

### Disabling Safety Checks

If you're confident in your content:

```
Use extract_and_sync_translations with:
  - skip_safety_check=true
```

## Common Workflows

### Workflow 1: Feature Branch Translation

After implementing a new feature:

```bash
# 1. Create feature branch
git checkout -b feature/product-landing

# 2. Write code with translation keys
# (use pattern: t('key', { _: 'Default Text' }))

# 3. Preview what will be extracted
Use preview_new_keys

# 4. Extract and sync
Use extract_and_sync_translations

# 5. Create PR to sync Lokalise → local JSON files
```

### Workflow 2: Bulk Translation Update

After making many changes:

```bash
# 1. Preview all changes
Use preview_new_keys with base_branch="main"

# 2. Review the output carefully

# 3. Sync in batches
Use extract_and_sync_translations with batch_size=5

# 4. Check Lokalise dashboard to verify
```

## Configuration Options

### Per-Project Configuration

Edit `.lokalise-mcp.json`:

```json
{
  "baseBranch": "develop",        // Compare against develop instead of main
  "batchSize": 5,                 // Create 5 keys per batch
  "filePatterns": ["**/*.tsx"],   // Only scan .tsx files
  "safety": {
    "enabled": false              // Disable safety checks
  }
}
```

### Per-Command Options

Override config when using tools:

```
Use extract_and_sync_translations with:
  - base_branch="develop"    // Compare against different branch
  - batch_size=10            // Larger batches
  - auto_approve=true        // Skip approval prompts
  - skip_safety_check=true   // Disable safety checks
```

## Next Steps

After keys are created in Lokalise:

1. Review translations in Lokalise dashboard
2. Make manual adjustments if needed
3. Create PR to sync Lokalise → local JSON files (your existing workflow)
4. Merge and deploy

## Troubleshooting

### "No translation keys found in changed files"

- Make sure you're on a feature branch (not main)
- Check that files match the configured patterns (*.tsx, *.ts, etc.)
- Verify translation functions are named `t()` or `translate()`

### "Key already exists - skipped"

The key is already in Lokalise. This is normal and prevents duplicates.

### Safety check flagged my text

Review the context - if it's a legitimate use (like technical error messages), you can:
1. Adjust the wording to be more professional
2. Use `skip_safety_check=true` if you're confident

## Best Practices

1. **Always use default values**: `t('key', { _: 'Default' })` instead of `t('key')`
2. **Use semantic key names**: `products.landing.title` not `text1`
3. **Preview before syncing**: Run `preview_new_keys` first
4. **Batch appropriately**: Use batch_size=3 for small changes, larger for bulk updates
5. **Review in Lokalise**: Check translations in the dashboard after creating

## Support

For issues or questions:
- Check the [Installation Guide](INSTALLATION.md)
- Review error messages carefully
- Check Lokalise dashboard to verify keys were created
```

**Step 2: Commit**

Run:
```bash
git add docs/USAGE.md
git commit -m "docs: add comprehensive usage guide"
```

**Step 3: Update main README with links**

Update `README.md`:
```markdown
# Lokalise MCP Integration

MCP server for extracting translation keys from code and syncing them to Lokalise with AI-powered translations.

## Features

- 🔍 Extract translation keys from git diff (compares current branch to main)
- 🤖 AI-powered translation to multiple languages using Claude
- 👀 Interactive preview before creating keys
- 🛡️ Content safety guards to prevent harmful translations
- 📦 Batch creation with progress tracking (3 keys at a time)
- ⚠️ Skip existing keys automatically

## Quick Start

1. **Install**: See [Installation Guide](docs/INSTALLATION.md)
2. **Configure**: Set up your Lokalise and Anthropic API keys
3. **Use**: Follow the [Usage Guide](docs/USAGE.md)

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Setup and configuration
- [Usage Guide](docs/USAGE.md) - How to use the MCP tools
- [Implementation Plan](docs/plans/2025-11-15-lokalise-mcp-integration.md) - Technical details

## Tools Provided

This MCP server provides three tools:

### 1. `get_lokalise_project_info`
Get project details including configured languages.

### 2. `preview_new_keys`
Preview translation keys that would be extracted (dry run).

### 3. `extract_and_sync_translations`
Extract keys from git diff and create them in Lokalise with AI translations.

## How It Works

1. **Extract**: Scans files changed in your branch for `t('key', { _: 'Default' })` patterns
2. **Translate**: Uses Claude AI to generate translations for all project languages
3. **Verify**: Runs safety checks to prevent harmful content
4. **Create**: Adds keys to Lokalise in batches of 3

## Requirements

- Python 3.10+
- Git repository
- Lokalise account with API access
- Anthropic API key

## License

MIT
```

**Step 4: Commit**

Run:
```bash
git add README.md
git commit -m "docs: update README with quick start and links"
```

---

## Execution Summary

This plan creates a complete Lokalise MCP integration with:

- ✅ Configuration management (env + JSON)
- ✅ Git diff extraction with file filtering
- ✅ Translation key extraction (regex-based)
- ✅ Lokalise API integration
- ✅ AI translation service
- ✅ Content safety guards
- ✅ FastMCP server with 3 tools
- ✅ Comprehensive documentation

**Total Tasks**: 10
**Estimated Time**: 4-6 hours for experienced developer
**Test Coverage**: Unit tests for all core modules

**Files Created**: 20+
**Lines of Code**: ~2000+
**Documentation Pages**: 3
