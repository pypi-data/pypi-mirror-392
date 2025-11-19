#!/bin/bash
# Script to run tests with coverage

set -e

echo "========================================"
echo "Airgap Transfer - Test Runner"
echo "========================================"
echo ""

# Check if pytest is installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "ERROR: pytest is not installed."
    echo ""
    echo "Install with:"
    echo "  pip install pytest pytest-cov"
    echo ""
    echo "Or install all dev dependencies:"
    echo "  pip install -e '.[dev]'"
    exit 1
fi

# Determine test mode
MODE="${1:-all}"

case "$MODE" in
    quick)
        echo "Running quick tests (no coverage)..."
        python3 -m pytest tests/ -v
        ;;
    coverage)
        echo "Running tests with coverage..."
        python3 -m pytest tests/ -v \
            --cov=airgap_transfer \
            --cov-report=html \
            --cov-report=term
        echo ""
        echo "Coverage report generated: htmlcov/index.html"
        ;;
    unit)
        echo "Running unit tests only..."
        python3 -m pytest tests/ -v \
            -k "not test_cli" \
            --cov=airgap_transfer \
            --cov-report=term
        ;;
    cli)
        echo "Running CLI tests only..."
        python3 -m pytest tests/test_cli.py -v
        ;;
    installer)
        echo "Running installer tests only..."
        python3 -m pytest tests/test_installer.py -v
        ;;
    *)
        echo "Running all tests with coverage..."
        python3 -m pytest tests/ -v \
            --cov=airgap_transfer \
            --cov-report=html \
            --cov-report=term \
            --cov-report=xml
        echo ""
        echo "Coverage reports generated:"
        echo "  - Terminal: (shown above)"
        echo "  - HTML: htmlcov/index.html"
        echo "  - XML: coverage.xml"
        ;;
esac

echo ""
echo "========================================"
echo "Tests Complete!"
echo "========================================"
