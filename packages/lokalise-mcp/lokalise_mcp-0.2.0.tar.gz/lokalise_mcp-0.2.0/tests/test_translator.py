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
    assert "Norwegian" in results


@pytest.mark.asyncio
async def test_translator_without_api_key():
    """Test that AITranslator works without API key (returns empty dict)."""
    # Create translator without API key
    translator = AITranslator(api_key=None)

    # Verify client is None
    assert translator.client is None
    assert translator.api_key is None

    # Test translate returns empty string when no client
    context = TranslationContext(
        key_name="products.title",
        source_text="Products"
    )

    result = await translator.translate(context, "Norwegian")
    assert result == ""

    # Test translate_to_languages returns empty dict when no client
    results = await translator.translate_to_languages(
        context=context,
        languages=["Norwegian", "Thai"]
    )
    assert results == {}

    # Test translate_batch returns empty list when no client
    contexts = [
        TranslationContext(key_name="products.title", source_text="Products"),
        TranslationContext(key_name="cart.title", source_text="Shopping Cart"),
    ]
    batch_results = await translator.translate_batch(
        contexts=contexts,
        target_language="Norwegian"
    )
    assert batch_results == []
