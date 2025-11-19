# Examples

This directory contains example scripts demonstrating various features of airgap-transfer.

## Available Examples

### 01_keyboard_transfer.py

Demonstrates keyboard-based file transfer using the KeyboardTransfer class.

**What it shows:**
- Create a KeyboardTransfer instance
- Generate transfer scripts
- Use speed presets (fast, normal, slow)
- Customize timing parameters

**Run:**
```bash
python3 examples/01_keyboard_transfer.py
```

### 02_qr_encode.py

Demonstrates QR code encoding for video-based file transfer.

**What it shows:**
- Create a QR encoder
- Get encoding statistics
- Encode files to QR code streams
- Progress tracking during encoding

**Run:**
```bash
# Requires QR code dependencies
pip install airgap-transfer[qrcode]

python3 examples/02_qr_encode.py
```

### 03_installer_usage.py

Demonstrates the installer module for generating standalone sender packages.

**What it shows:**
- Generate complete installation bundles
- Create standalone single-file senders
- Understand the transfer workflow
- Bundle information and management

**Run:**
```bash
python3 examples/03_installer_usage.py
```

## Creating Test Files

To test the examples, create some test files first:

```bash
# Create a simple text file
echo "Hello from airgap-transfer!" > test.txt

# Create a larger binary file
dd if=/dev/urandom of=test.bin bs=1024 count=10

# Create a PDF (if you have a PDF tool)
echo "Sample PDF content" > sample.txt
# or use an existing PDF file
```

## Requirements

Install airgap-transfer with the appropriate dependencies:

```bash
# For keyboard transfer examples (01)
pip install airgap-transfer

# For QR code examples (02)
pip install airgap-transfer[qrcode]

# For installer examples (03)
pip install airgap-transfer

# For all examples
pip install airgap-transfer[all]
```

## More Information

For more examples and documentation:
- CLI help: `airgap --help`
- Main README: [../README.md](../README.md)
- Chinese README: [../README_CN.md](../README_CN.md)
- Refactoring plan: [../REFACTORING_PLAN.md](../REFACTORING_PLAN.md)
