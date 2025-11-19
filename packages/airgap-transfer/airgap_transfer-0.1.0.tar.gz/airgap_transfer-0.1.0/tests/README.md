# Tests

This directory contains the test suite for airgap-transfer.

## Running Tests

### Prerequisites

Install the package with dev dependencies:

```bash
pip install -e ".[dev]"
```

Or install test dependencies separately:

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# Simple test run
pytest

# Verbose output
pytest -v

# With coverage report
pytest --cov=airgap_transfer --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_installer.py

# Run specific test
pytest tests/test_installer.py::TestSenderPackager::test_generate_creates_all_files
```

## Test Structure

```
tests/
├── __init__.py                  # Test package init
├── conftest.py                  # Pytest configuration and fixtures
├── test_keyboard_sender.py      # Tests for keyboard transfer
├── test_qr_encoder.py           # Tests for QR encoding
├── test_qr_decoder.py           # Tests for QR decoding
├── test_installer.py            # Tests for installer module
├── test_cli.py                  # Tests for CLI commands
├── test_utils.py                # Tests for utility functions
└── fixtures/                    # Test data
    ├── test_files/              # Sample files for testing
    └── test_videos/             # Sample videos (for QR decode tests)
```

## Test Coverage

Test coverage is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=airgap_transfer --cov-report=html --cov-report=term"
```

Coverage reports are generated in:
- Terminal: Displayed after test run
- HTML: `htmlcov/index.html`

## Writing Tests

### Example Test

```python
import pytest
from airgap_transfer import KeyboardTransfer

def test_keyboard_transfer_init(tmp_path):
    """Test KeyboardTransfer initialization."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    transfer = KeyboardTransfer(str(test_file))

    assert transfer.file_path.exists()
```

### Using Fixtures

```python
def test_with_fixture(sample_text_file):
    """Use a shared fixture from conftest.py."""
    assert sample_text_file.exists()
```

### Mocking External Dependencies

```python
from unittest.mock import patch, MagicMock

@patch('airgap_transfer.keyboard.sender._lazy_import_pynput')
def test_with_mock(mock_import):
    """Test with mocked pynput."""
    mock_controller = MagicMock()
    mock_import.return_value = (lambda: mock_controller, MagicMock())

    # Test code here
```

## Test Categories

### Unit Tests
- `test_keyboard_sender.py` - KeyboardTransfer class
- `test_qr_encoder.py` - QREncoder class
- `test_qr_decoder.py` - QRDecoder class
- `test_installer.py` - SenderPackager class
- `test_utils.py` - Utility functions

### Integration Tests
- `test_cli.py` - CLI command integration

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Pushes to main branch
- Tagged releases

See `.github/workflows/ci.yml` for CI configuration.

## Coverage Goals

Target coverage: **80%+**

Current coverage can be checked by running:
```bash
pytest --cov=airgap_transfer --cov-report=term-missing
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed in editable mode:
```bash
pip install -e .
```

### Missing Dependencies

For QR code tests, install optional dependencies:
```bash
pip install airgap-transfer[qrcode]
```

For all test dependencies:
```bash
pip install airgap-transfer[dev]
```

### Skipped Tests

Some tests may be skipped if optional dependencies are not installed. This is expected behavior.

## Contributing

When adding new features:
1. Write tests for new functionality
2. Ensure existing tests still pass
3. Maintain or improve coverage
4. Follow existing test patterns

For more information, see [CONTRIBUTING.md](../CONTRIBUTING.md).
