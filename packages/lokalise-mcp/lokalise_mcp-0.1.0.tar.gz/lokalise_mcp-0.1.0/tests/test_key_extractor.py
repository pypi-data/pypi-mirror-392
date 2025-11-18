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
