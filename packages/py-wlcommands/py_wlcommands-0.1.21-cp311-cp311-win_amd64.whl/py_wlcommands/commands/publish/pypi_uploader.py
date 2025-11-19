"""PyPI uploading for publish command."""

import subprocess
from pathlib import Path

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info


class PyPIUploader:
    """Handle PyPI uploading operations for the publish command."""

    def upload_to_pypi(self, repository: str, dist_files, username=None, password=None):
        """Upload distribution files to PyPI."""
        try:
            # Check if twine is available
            subprocess.run(
                ["twine", "--version"],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise CommandError(
                "twine is not installed. Please install it with 'pip install twine'"
            )

        # Build twine command
        cmd = ["twine", "upload"]
        if repository != "pypi":
            cmd.extend(["--repository", repository])
        if username:
            cmd.extend(["--username", username])
        if password:
            cmd.extend(["--password", password])

        # Add all dist files
        for f in dist_files:
            cmd.append(str(f))

        log_info(f"Uploading to {repository} with command: {' '.join(cmd)}")
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=False,
            )
        except subprocess.CalledProcessError as e:
            raise CommandError(f"Upload failed: {e}")
