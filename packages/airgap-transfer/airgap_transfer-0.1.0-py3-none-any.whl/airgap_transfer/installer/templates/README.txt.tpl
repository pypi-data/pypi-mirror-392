================================================================================
Airgap Transfer - QR Sender Installation Package
================================================================================

Version: {version}
Generated: {timestamp}

This package contains a standalone QR code sender tool that can be installed
in air-gapped environments for sending files via QR code video streams.

--------------------------------------------------------------------------------
CONTENTS
--------------------------------------------------------------------------------

1. qr_sender.py     - Standalone QR code sender script
2. install.sh       - Installation script (Linux/macOS)
3. README.txt       - This file

--------------------------------------------------------------------------------
QUICK START
--------------------------------------------------------------------------------

Option 1: Automatic Installation (Linux/macOS)
------------------------------------------------
Run the installation script:

    bash install.sh

This will install qr_sender.py to ~/airgap_tools/


Option 2: Manual Installation
------------------------------------------------
1. Copy qr_sender.py to your desired location
2. Make it executable: chmod +x qr_sender.py
3. Ensure Python 3.8+ and qrcode library are installed


--------------------------------------------------------------------------------
DEPENDENCIES
--------------------------------------------------------------------------------

The QR sender requires:
- Python 3.8 or higher
- qrcode library with PIL support

To install the qrcode library:

    pip install qrcode[pil]

Or if pip is not in PATH:

    python3 -m pip install qrcode[pil]


--------------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------------

Basic usage:

    python3 qr_sender.py <file_path> [first_frame_duration]

Arguments:
  file_path              File to encode and send (required)
  first_frame_duration   How long to display first frame in frames (default: 3)


Example 1: Display QR codes with ffplay
-----------------------------------------
python3 qr_sender.py myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -


Example 2: Save QR codes as video
----------------------------------
python3 qr_sender.py myfile.pdf 5 | ffmpeg -framerate 1 -f image2pipe -i - output.mp4


Example 3: Custom frame rate
-----------------------------
# Faster display (2 fps)
python3 qr_sender.py myfile.pdf 5 | ffplay -framerate 2 -f image2pipe -i -


--------------------------------------------------------------------------------
RECEIVING FILES
--------------------------------------------------------------------------------

To receive files on the other side, you need the full airgap-transfer package:

1. Install from PyPI:
   pip install airgap-transfer[qrcode]

2. Decode video to file:
   airgap qr-decode recording.mp4 output.pdf


--------------------------------------------------------------------------------
TROUBLESHOOTING
--------------------------------------------------------------------------------

Q: "ImportError: No module named 'qrcode'"
A: Install qrcode library: pip install qrcode[pil]

Q: "ImportError: No module named 'PIL'"
A: Install Pillow: pip install Pillow
   Or reinstall qrcode with PIL: pip install qrcode[pil]

Q: QR codes are too small/large
A: Edit qr_sender.py and adjust DEFAULT_BOX_SIZE (default: 10)

Q: Video playback is too fast/slow
A: Adjust the -framerate parameter in ffplay/ffmpeg command


--------------------------------------------------------------------------------
MORE INFORMATION
--------------------------------------------------------------------------------

Project homepage:
  https://github.com/RLHQ/airgap-transfer

Documentation:
  https://github.com/RLHQ/airgap-transfer/blob/main/README.md

Report issues:
  https://github.com/RLHQ/airgap-transfer/issues


================================================================================
