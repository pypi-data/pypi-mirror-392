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
