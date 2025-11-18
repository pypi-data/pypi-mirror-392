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
    mock_lokalise_api.project_languages.return_value = [
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
    mock_lokalise_api.keys.return_value = []  # No existing keys
    mock_lokalise_api.create_keys.return_value = Mock(key_id=123)

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


@pytest.mark.asyncio
async def test_create_translation_task(mock_lokalise_api):
    """Test creating a translation task in Lokalise."""
    # Mock project info to get base language
    mock_project = Mock()
    mock_project.project_id = "test_project"
    mock_project.name = "Test Project"
    mock_project.base_lang_iso = "en"
    mock_lokalise_api.project.return_value = mock_project

    # Mock task creation response
    mock_task = Mock()
    mock_task.task_id = 456
    mock_task.title = "Auto-translate new keys"
    mock_lokalise_api.create_task.return_value = mock_task

    client = LokaliseClient(api_token="test_token", project_id="test_project")

    result = await client.create_translation_task(
        key_ids=[123, 124, 125],
        target_languages=["no", "th", "en"],
        task_title="Auto-translate new keys"
    )

    # Verify task was created with correct parameters
    mock_lokalise_api.create_task.assert_called_once()
    call_args = mock_lokalise_api.create_task.call_args

    assert call_args[0][0] == "test_project"
    task_data = call_args[0][1]

    assert task_data["title"] == "Auto-translate new keys"
    assert task_data["task_type"] == "automatic_translation"
    assert task_data["keys"] == [123, 124, 125]
    assert task_data["auto_close_task"] is True
    assert task_data["auto_close_items"] is True
    assert task_data["apply_ai_tm100_matches"] is True
    assert task_data["save_ai_translation_to_tm"] is True

    # Verify base language (en) is excluded from target languages
    languages = task_data["languages"]
    assert len(languages) == 2  # Only no and th, en excluded
    assert {"language_iso": "no", "users": []} in languages
    assert {"language_iso": "th", "users": []} in languages

    # Verify result is the task object
    assert result.task_id == 456
