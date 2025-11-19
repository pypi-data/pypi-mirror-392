# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**airgap-transfer** is a Python package for bi-directional file transfer in air-gapped and isolated environments (VDI, bastion hosts, air-gapped networks). It supports two transfer methods:

1. **Keyboard Transfer**: Simulates keyboard typing to transfer files via terminal input
2. **QR Code Transfer**: Encodes files as QR code video streams for screen sharing/recording

**Current Status**: v0.1.0 (beta) - not yet published to PyPI

## Development Commands

### Package Management

**IMPORTANT**: This project uses `uv` for package management. Always use `uv` commands instead of `pip`.

```bash
# Install base package (keyboard transfer only)
uv pip install -e .

# Install with QR code support (recommended for development)
uv pip install -e ".[all]"

# Install with all dependencies including dev tools
uv pip install -e ".[all,dev]"

# Sync environment (recommended)
uv sync
uv sync --extra all --extra dev
```

### Testing

**Use `uv run` to execute Python commands:**

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=airgap_transfer --cov-report=html --cov-report=term

# Run specific test file
uv run pytest tests/test_keyboard_sender.py

# Run specific test function
uv run pytest tests/test_keyboard_sender.py::test_function_name
```

### Code Quality

**Use `uv run` for all Python tools:**

```bash
# Format code (line length: 100)
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

### Building

```bash
# Build distribution packages
uv run python -m build

# This generates dist/airgap_transfer-0.1.0.tar.gz and .whl
```

### CLI Usage

**Development: Use `uv run` prefix**

```bash
# Keyboard transfer
uv run airgap send myfile.pdf
uv run airgap send myfile.pdf --output /tmp/received.pdf
uv run airgap send myfile.pdf --fast    # Speed presets: slow, normal, fast

# QR code transfer
uv run airgap qr-encode myfile.pdf | ffplay -framerate 1 -f image2pipe -i -
uv run airgap qr-decode recording.mp4 output.pdf
uv run airgap qr-decode recording.mp4 output.pdf --verify original.pdf

# Installer (generate and transfer installation bundle)
uv run airgap install --generate        # Generate sender-bundle/
uv run airgap install --transfer        # Transfer self-contained install.sh via keyboard
```

## Architecture

### Package Structure

```
src/airgap_transfer/
├── __init__.py           # Package entry point with lazy imports
├── __version__.py        # Version info
├── keyboard/             # Keyboard transfer module
│   └── sender.py        # KeyboardTransfer class - generates bash scripts
├── qrcode/              # QR code transfer module
│   ├── encoder.py       # QREncoder class - encodes files to QR PNG stream
│   └── decoder.py       # QRDecoder class - decodes from video files
├── cli/                 # Command-line interface
│   ├── main.py          # CLI entry point with subcommand routing
│   ├── send.py          # 'send' subcommand
│   ├── qr_encode.py     # 'qr-encode' subcommand
│   ├── qr_decode.py     # 'qr-decode' subcommand
│   └── install.py       # 'install' subcommand
├── utils/               # Shared utilities
│   ├── encoding.py      # Base64 encoding utilities
│   ├── checksum.py      # SHA256 checksum calculation
│   └── constants.py     # Timing delays, chunk sizes, etc.
└── installer/           # Installation bundle generation (WIP)
    └── packager.py      # SenderPackager class
```

### Key Design Patterns

**1. Lazy Imports for Optional Dependencies**
- Base package only requires `pynput` (keyboard transfer)
- QR code features require `qrcode`, `opencv-python`, `pyzbar` (optional)
- `__init__.py` uses `__getattr__` for lazy module loading
- CLI modules use try/except to gracefully handle missing dependencies

**2. Keyboard Transfer Flow**
- `KeyboardTransfer.generate_script()` creates self-contained bash script with:
  - Base64-encoded file data
  - Expected SHA256 checksum
  - Decoder logic (uses `base64 -d`)
  - Verification logic (supports `sha256sum` or `shasum`)
- `KeyboardTransfer.send()` uses `pynput` to simulate typing the script
- Speed presets in `utils/constants.py`: slow, normal, fast (different char/line delays)
- Script auto-executes on remote terminal after typing

**3. QR Code Transfer Flow**
- **Encoding**: `QREncoder` splits file into chunks, encodes as QR codes, outputs PNG stream
  - Each QR contains: `{chunk_number}/{total_chunks}|{base64_data}`
  - First frame held longer (DEFAULT_FIRST_FRAME_DURATION) for setup
  - Determines optimal QR version dynamically from data size
- **Decoding**: `QRDecoder` processes video frame-by-frame
  - Detects QR codes using `pyzbar`
  - Handles duplicate frames and missing chunks
  - Reassembles data and verifies against optional original file

**4. CLI Architecture**
- Main entry point: `cli/main.py:main()`
- Each subcommand has `register_subcommand(subparsers)` function
- Subcommands set `args.func` to their handler function
- Error handling in main catches ImportError for missing optional deps

**5. Installer Bundle Flow**
- **Generation**: `SenderPackager.generate()` creates `sender-bundle/` with:
  - `install.sh`: Self-contained installation script (includes embedded `qr_sender.py`)
  - `qr_sender.py`: Standalone QR encoder script (for reference)
  - `README.txt`: Usage instructions
- **Transfer**: `SenderPackager.transfer_to_remote()` uses keyboard transfer to send `install.sh`
  - **Only ONE file needs to be transferred** (install.sh is self-contained)
  - Script extracts and installs `qr_sender.py` to `~/airgap_tools/`
  - No dependency on external files during installation

### Testing Strategy

- Test fixtures in `tests/fixtures/test_files/`
- Shared fixtures in `tests/conftest.py` (sample files, directories)
- Target: >80% code coverage
- Unit tests for each module: encoder, decoder, keyboard sender, CLI, utils

## Important Constraints

**Python Compatibility**:
- **Development environment**: Python 3.9+ (see pyproject.toml)
  - Type hints can use modern syntax in Python 3.9+ (e.g., `list[str]`, `dict[str, int]`)
  - Avoid syntax/features from 3.10+ for wider compatibility
- **VDI/Air-gapped environments**: Python 3.8 compatibility required
  - QR code sender scripts must work with Python 3.8
  - Only depends on `qrcode` package (no opencv-python or pyzbar)
  - Use `python3` command (not `python`)
  - Scripts in `src/airgap_transfer/qrcode/encoder.py` must be Python 3.8 compatible

**Package Management**:
- **Development**: Use `uv` for all package management and Python execution
  - Install: `uv pip install` or `uv sync`
  - Run commands: `uv run <command>`
  - Execute Python: `uv run python` or `uv run airgap`
- **VDI/Air-gapped**: Use system `python3` and minimal dependencies

**Security Considerations**:
- Files are NOT encrypted by default
- Keyboard transfer creates temporary bash script visible in history
- Always include SHA256 checksum verification
- Scripts use heredoc with `'END_OF_SCRIPT'` to prevent code injection

**Performance Expectations**:
- Keyboard transfer: ~10KB/minute (varies by connection latency)
- QR transfer: ~10-50KB in 30s-2min (depends on video quality)
- Files >100KB not recommended without compression

**Dependencies**:
- Keep base dependencies minimal (only `pynput`)
- All QR-related deps must be optional
- Use lazy imports to avoid import-time failures

## Development Guidelines

**Code Style**:
- Black formatting: line length 100
- Type hints required (Google-style docstrings)
- Follow PEP 8

**Commit Messages** (conventional commits):
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation
- `test:` tests
- `refactor:` code refactoring
- `chore:` maintenance

**Adding New Features**:
1. Update appropriate module in `src/airgap_transfer/`
2. Add CLI subcommand if user-facing (in `cli/`)
3. Write unit tests in `tests/`
4. Update README.md examples
5. Update CHANGELOG.md

**Testing New CLI Commands**:
```bash
# Test CLI in development mode (use uv run)
uv run python -m airgap_transfer.cli.main send test.txt

# Or use installed command with uv run
uv run airgap send test.txt
```

## Roadmap Context

**v0.2.0 (Planned)**:
- Installer module for generating standalone sender packages
- Configuration file support
- Enhanced documentation

**v0.3.0 (Future)**:
- Batch transfer support
- Resume/retry functionality
- Compression support
- Encryption options

## Common Pitfalls

1. **pynput X server requirement**: Import `pynput` lazily to avoid requiring X11/display at import time
2. **Optional dependencies**: Always wrap QR imports in try/except; handle gracefully in CLI
3. **Python version compatibility**:
   - Development requires Python 3.9+ due to pynput's macOS dependencies (pyobjc-core)
   - VDI/air-gapped QR sender must work with Python 3.8 (use `python3` command)
4. **Package management**: Always use `uv run` for development commands; don't use bare `python` or `pip`
5. **VDI QR dependencies**: QR sender scripts in VDI only need `qrcode` package, not opencv/pyzbar
6. **Base64 line splitting**: Keyboard transfer splits at 76 chars (standard) for reliable terminal handling
7. **QR chunk size**: DEFAULT_QR_CHUNK_SIZE balances QR version vs number of frames
