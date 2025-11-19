"""Package building for publish command."""

import shutil
import subprocess
from pathlib import Path

from ...exceptions import CommandError
from ...utils.logging import log_info


class PackageBuilder:
    """Handle package building operations for the publish command."""

    def build_distribution_packages(self) -> None:
        """Build distribution packages using wl build dist command."""
        log_info("Building distribution packages with 'wl build dist'...")
        log_info("使用 'wl build dist' 构建分发包...", lang="zh")

        # Clean previous builds
        dist_dir = Path("dist")
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
            dist_dir.mkdir(exist_ok=True)

        try:
            # Use wl build dist command to build distribution packages
            # This ensures we use the same build process as the user would
            result = subprocess.run(
                ["wl", "build", "dist"],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            if result.stdout:
                log_info(f"Build output: {result.stdout}")

            log_info("✓ Distribution packages built successfully with 'wl build dist'")
            log_info("✓ 分发包通过 'wl build dist' 成功构建", lang="zh")

        except subprocess.CalledProcessError as e:
            raise CommandError(
                f"Build failed: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}"
            )

    def get_dist_files(self):
        """Get distribution files from dist directory."""
        dist_dir = Path("dist")
        if not dist_dir.exists():
            dist_dir.mkdir(exist_ok=True)
            return []

        return list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
