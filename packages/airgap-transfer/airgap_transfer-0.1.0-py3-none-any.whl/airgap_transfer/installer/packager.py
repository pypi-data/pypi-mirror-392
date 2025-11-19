"""
Sender packager for generating standalone installation bundles.

This module creates standalone sender packages that can be transferred
to air-gapped environments.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..__version__ import __version__


class SenderPackager:
    """
    Package the QR sender tool for installation in air-gapped environments.

    This class generates standalone installation bundles containing:
    - qr_sender.py: Standalone QR encoder script
    - install.sh: Installation script
    - README.txt: Usage instructions
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize sender packager.

        Args:
            output_dir: Directory to output the installation bundle.
                       Defaults to './sender-bundle'
        """
        self.output_dir = Path(output_dir or "sender-bundle")
        self.templates_dir = Path(__file__).parent / "templates"
        self.version = __version__
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    def _load_template(self, template_name: str, **kwargs) -> str:
        """
        Load a template file and substitute variables.

        Args:
            template_name: Name of template file (e.g., 'qr_sender.py.tpl')
            **kwargs: Additional variables to substitute

        Returns:
            Template content with variables substituted
        """
        template_path = self.templates_dir / template_name
        with open(template_path, 'r') as f:
            content = f.read()

        # Substitute standard variables
        content = content.replace("{version}", self.version)
        content = content.replace("{timestamp}", self.timestamp)

        # Substitute additional variables
        for key, value in kwargs.items():
            content = content.replace(f"{{{key}}}", value)

        return content

    def generate(self, clean: bool = True) -> Path:
        """
        Generate the installation bundle.

        Args:
            clean: If True, remove existing output directory first

        Returns:
            Path to the generated bundle directory

        Raises:
            FileExistsError: If output directory exists and clean=False
        """
        # Clean output directory if requested
        if self.output_dir.exists():
            if clean:
                shutil.rmtree(self.output_dir)
            else:
                raise FileExistsError(
                    f"Output directory already exists: {self.output_dir}\n"
                    "Use clean=True to overwrite or choose a different output directory."
                )

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate files from templates
        self._generate_qr_sender()
        self._generate_install_script()
        self._generate_readme()

        return self.output_dir

    def _generate_qr_sender(self) -> Path:
        """Generate the standalone QR sender script."""
        content = self._load_template("qr_sender.py.tpl")
        output_path = self.output_dir / "qr_sender.py"

        with open(output_path, 'w') as f:
            f.write(content)

        # Make executable
        output_path.chmod(0o755)

        return output_path

    def _generate_install_script(self) -> Path:
        """Generate the installation script with embedded QR sender."""
        # First load the QR sender content
        qr_sender_content = self._load_template("qr_sender.py.tpl")

        # Then load the bootstrap script and embed the QR sender
        content = self._load_template("bootstrap.sh.tpl", qr_sender_content=qr_sender_content)
        output_path = self.output_dir / "install.sh"

        with open(output_path, 'w') as f:
            f.write(content)

        # Make executable
        output_path.chmod(0o755)

        return output_path

    def _generate_readme(self) -> Path:
        """Generate the README file."""
        content = self._load_template("README.txt.tpl")
        output_path = self.output_dir / "README.txt"

        with open(output_path, 'w') as f:
            f.write(content)

        return output_path

    def generate_standalone(self, output_file: Optional[str] = None) -> Path:
        """
        Generate a single standalone QR sender script.

        This creates just the qr_sender.py file without the full bundle.

        Args:
            output_file: Output file path. Defaults to './qr_sender_standalone.py'

        Returns:
            Path to the generated file
        """
        output_path = Path(output_file or "qr_sender_standalone.py")
        content = self._load_template("qr_sender.py.tpl")

        with open(output_path, 'w') as f:
            f.write(content)

        # Make executable
        output_path.chmod(0o755)

        return output_path

    def get_bundle_info(self) -> dict:
        """
        Get information about the bundle.

        Returns:
            Dictionary with bundle information
        """
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "output_dir": str(self.output_dir),
            "templates_dir": str(self.templates_dir),
            "files": [
                "qr_sender.py",
                "install.sh",
                "README.txt",
            ],
        }

    def transfer_to_remote(
        self,
        countdown: int = 5,
        char_delay: float = 0.005,
        line_delay: float = 0.03,
    ):
        """
        Transfer the installation bundle to a remote system via keyboard input.

        This generates the bundle and uses KeyboardTransfer to send the
        self-contained installation script to the remote terminal.

        The install.sh script is self-contained with embedded QR sender,
        so only ONE file needs to be transferred.

        Args:
            countdown: Countdown before starting transfer
            char_delay: Delay between characters
            line_delay: Delay between lines

        Raises:
            ImportError: If keyboard transfer dependencies not available
        """
        from ..keyboard import KeyboardTransfer

        # Generate bundle first
        bundle_path = self.generate()

        # Transfer the install script (which now contains embedded qr_sender.py)
        install_script = bundle_path / "install.sh"

        print(f"Preparing to transfer self-contained installation script via keyboard...")
        print(f"Bundle location: {bundle_path}")
        print("")
        print("Instructions:")
        print("1. Switch to your remote terminal")
        print("2. Create a directory for the bundle: mkdir -p ~/airgap-bundle && cd ~/airgap-bundle")
        print("3. Prepare to receive the install script: cat > install.sh")
        print("4. After the transfer, press Ctrl+D to save")
        print("5. Run the installer: bash install.sh")
        print("")
        print("Note: The install.sh script is self-contained and includes the QR sender.")
        print("      No additional files need to be transferred!")
        print("")
        print(f"Transfer will start in {countdown} seconds...")
        print("")

        # Use keyboard transfer for install script
        transfer = KeyboardTransfer(
            file_path=str(install_script),
            output_path="install.sh",
            char_delay=char_delay,
            line_delay=line_delay,
        )
        transfer.send(countdown=countdown, auto_execute=False)

        print("")
        print("Transfer complete!")
        print("")
        print("Next steps in the remote terminal:")
        print("1. Press Ctrl+D to save the file")
        print("2. Run the installer: bash install.sh")
        print("3. The QR sender will be installed to ~/airgap_tools/qr_sender.py")
