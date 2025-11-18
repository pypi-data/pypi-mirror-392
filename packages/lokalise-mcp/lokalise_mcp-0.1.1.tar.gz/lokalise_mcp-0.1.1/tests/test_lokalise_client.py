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
