import pytest
from unittest.mock import Mock, MagicMock, patch
from lokalise_mcp.safety import SafetyGuard, SafetyCheckResult


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API for safety checks."""
    with patch('lokalise_mcp.safety.Anthropic') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.mark.asyncio
async def test_safe_text_passes(mock_anthropic):
    """Test that safe text passes safety check."""
    mock_content = MagicMock()
    mock_content.text = "SAFE"
    mock_response = MagicMock()
    mock_response.content = [mock_content]

    # Mock the client's messages.create method
    mock_anthropic.messages.create.return_value = mock_response

    guard = SafetyGuard(api_key="test_key")
    result = await guard.check_source_text("Save Changes")

    assert result.is_safe is True
    assert len(result.flags) == 0


@pytest.mark.asyncio
async def test_unsafe_text_flagged(mock_anthropic):
    """Test that unsafe text is flagged."""
    mock_content = MagicMock()
    mock_content.text = "UNSAFE: Contains profanity"
    mock_response = MagicMock()
    mock_response.content = [mock_content]

    # Mock the client's messages.create method
    mock_anthropic.messages.create.return_value = mock_response

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
    mock_content = MagicMock()
    mock_content.text = "APPROVED"
    mock_response = MagicMock()
    mock_response.content = [mock_content]

    # Mock the client's messages.create method
    mock_anthropic.messages.create.return_value = mock_response

    guard = SafetyGuard(api_key="test_key")
    result = await guard.check_translation(
        original="Save Changes",
        translated="Lagre endringer",
        language="Norwegian"
    )

    assert result.is_safe is True
