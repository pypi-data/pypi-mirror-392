# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-05

### Added

- Initial release of airgap-transfer
- Keyboard-based file transfer (`airgap send`)
  - Transfer files via simulated keyboard input
  - Speed presets (slow, normal, fast)
  - Auto-execution support
  - SHA256 checksum verification
- QR code-based file transfer
  - File encoding to QR code stream (`airgap qr-encode`)
  - Video decoding to file (`airgap qr-decode`)
  - High error correction support
  - Progress tracking
- Unified CLI interface (`airgap` command)
- Comprehensive utility functions
  - Base64 encoding/decoding
  - SHA256 checksums
  - File comparison
- Professional project structure
  - Type hints throughout
  - Modular design
  - Clean API
- Documentation
  - README with usage examples
  - API documentation
  - Migration guide from legacy scripts

### Changed

- Refactored from standalone scripts to professional library
- Improved error handling and validation
- Enhanced progress reporting

### Deprecated

- Legacy scripts (transfer_file_v2.py, qrtest_pipe.py, qrdecode_video.py)
  - Still available but not actively maintained
  - Use new `airgap` CLI instead

## [Unreleased]

### Planned for v0.2.0

- Installer module for air-gapped environments
- Standalone sender package generation
- Automated sender installation via keyboard transfer
- Batch file transfer support
- Configuration file support

### Planned for v0.3.0

- Resume/retry functionality
- Compression support
- Encryption options
- Enhanced error recovery
