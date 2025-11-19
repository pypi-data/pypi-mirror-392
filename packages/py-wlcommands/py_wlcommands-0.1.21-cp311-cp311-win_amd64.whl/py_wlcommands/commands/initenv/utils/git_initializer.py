"""Git initializer utility."""

import os
import shutil
import subprocess
from pathlib import Path

from ....utils.logging import log_info
from .exceptions import GitInitializationError
from .log_manager import performance_monitor


class GitInitializer:
    """Git repository initializer."""

    def __init__(self, env: dict[str, str]) -> None:
        self.env = env

    @performance_monitor
    def initialize(self) -> None:
        """Initialize Git repository if it doesn't exist."""
        # Copy .gitignore template if it doesn't exist
        gitignore_path = Path(".gitignore")
        # Only copy template if .gitignore doesn't exist and we're not in a test environment
        if not gitignore_path.exists() and not os.environ.get("PYTEST_CURRENT_TEST"):
            self._copy_gitignore_template()

        if not Path(".git").exists():
            log_info("Initializing Git repository...")
            log_info("初始化Git仓库...", lang="zh")
            try:
                subprocess.run(
                    ["git", "init"], check=True, capture_output=False, env=self.env
                )
                log_info("✓ Git repository initialized")
                log_info("✓ Git仓库初始化完成", lang="zh")
            except subprocess.CalledProcessError as e:
                log_info("Warning: Failed to initialize Git repository")
                log_info("警告: 初始化Git仓库失败", lang="zh")
                raise GitInitializationError(
                    f"Failed to initialize Git repository: {e}"
                )
        else:
            log_info("Git repository already exists, skipping initialization")
            log_info("Git仓库已存在，跳过初始化", lang="zh")

    def _copy_gitignore_template(self) -> None:
        """Copy .gitignore template from vendors to project root."""
        try:
            # Calculate path to vendors/git/.gitignore relative to this file
            # File is in src/py_wlcommands/commands/initenv/utils/
            # vendors dir is in src/py_wlcommands/
            # So we need to go up 4 levels
            template_path = (
                Path(__file__).parent.parent.parent.parent
                / "vendors"
                / "git"
                / ".gitignore"
            )

            log_info(f"Looking for .gitignore template at: {template_path}")

            if template_path.exists():
                shutil.copy2(template_path, ".gitignore")
                log_info("✓ .gitignore template copied successfully")
                log_info("✓ .gitignore 模板复制成功", lang="zh")
            else:
                log_info(f"Warning: .gitignore template not found at {template_path}")
                log_info(f"警告: 未找到 .gitignore 模板 {template_path}", lang="zh")
        except Exception as e:
            log_info(f"Warning: Failed to copy .gitignore template: {e}")
            log_info(f"警告: 复制 .gitignore 模板失败: {e}", lang="zh")
