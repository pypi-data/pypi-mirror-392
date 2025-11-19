#!/bin/bash
# Airgap Transfer - Installation Script for Air-Gapped Environments
# Version: {version}
# Generated: {timestamp}
#
# This script installs the QR sender tool in an air-gapped environment.
# The QR sender script is embedded in this file, no additional files needed.

set -e

INSTALL_DIR="$HOME/airgap_tools"
SCRIPT_NAME="qr_sender.py"

echo "========================================"
echo "Airgap Transfer - QR Sender Installation"
echo "========================================"
echo ""
echo "Version: {version}"
echo "Install directory: $INSTALL_DIR"
echo ""

# Create installation directory
echo "[1/3] Creating installation directory..."
mkdir -p "$INSTALL_DIR"
echo "  ✓ Created: $INSTALL_DIR"
echo ""

# Extract embedded QR sender script
echo "[2/3] Installing QR sender script..."
cat > "$INSTALL_DIR/$SCRIPT_NAME" <<'END_OF_QR_SENDER'
{qr_sender_content}
END_OF_QR_SENDER

chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
echo "  ✓ Installed: $INSTALL_DIR/$SCRIPT_NAME"
echo ""

# Check Python and dependencies
echo "[3/3] Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "  ⚠ WARNING: python3 not found in PATH"
    echo "  Please ensure Python 3.8+ is installed."
else
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{{print $2}}')
    echo "  ✓ Python version: $PYTHON_VERSION"
fi

# Check for qrcode library
if python3 -c "import qrcode" 2>/dev/null; then
    echo "  ✓ qrcode library is installed"
else
    echo "  ⚠ WARNING: qrcode library not found"
    echo "  Install with: pip install qrcode[pil]"
    echo "  Or: python3 -m pip install qrcode[pil]"
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Usage:"
echo "  python3 $INSTALL_DIR/$SCRIPT_NAME <file> [duration]"
echo ""
echo "Examples:"
echo "  # Display QR codes with ffplay (1 fps)"
echo "  python3 $INSTALL_DIR/$SCRIPT_NAME myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -"
echo ""
echo "  # Save as video"
echo "  python3 $INSTALL_DIR/$SCRIPT_NAME myfile.pdf 5 | ffmpeg -framerate 1 -f image2pipe -i - output.mp4"
echo ""
echo "For more information, visit:"
echo "  https://github.com/RLHQ/airgap-transfer"
echo ""
