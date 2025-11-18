"""Configuration management for Lokalise MCP."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file before defining Config
# Use explicit path to handle cases where cwd != project root
_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path)


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
        # ANTHROPIC_API_KEY is now optional

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
        if "translationPatterns" in data:
            if "functions" in data["translationPatterns"]:
                config.translation_functions = data["translationPatterns"]["functions"]
            if "defaultParam" in data["translationPatterns"]:
                config.default_param_name = data["translationPatterns"]["defaultParam"]

    return config
