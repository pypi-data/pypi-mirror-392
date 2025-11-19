"""Project initializer coordinator."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from ....utils.logging import log_info
from .cargo_sync import sync_toml_files
from .config_manager import ConfigManager
from .git_initializer import GitInitializer
from .i18n_manager import I18nManager
from .log_manager import LogManager
from .project_structure import ProjectStructureSetup
from .pyproject_generator import PyProjectGenerator
from .rust_initializer import RustInitializer
from .venv_manager import VenvManager


class Initializer:
    """Coordinator for project initialization."""

    def __init__(self, env: dict[str, str]) -> None:
        self.env = env
        self.project_name = Path.cwd().name
        self.config_manager = ConfigManager()
        self.i18n_manager = I18nManager()
        self.log_manager = LogManager()

        # Initialize sub-components
        self.git_initializer = GitInitializer(env)
        self.project_structure_setup = ProjectStructureSetup()
        self.rust_initializer = RustInitializer()
        self.venv_manager = VenvManager(env)

    def check_uv_installed(self) -> None:
        """Check if uv is installed."""
        try:
            subprocess.run(
                ["uv", "--version"], check=True, capture_output=True, env=self.env
            )
            log_info("✓ uv command found.")
            log_info("✓ 找到 uv 命令。", lang="zh")
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
            from ....exceptions import CommandError

            raise CommandError(
                "uv command not found. Please install uv first (e.g., pip install uv) and try again."
            )

    def init_git(self) -> None:
        """Initialize Git repository."""
        self.git_initializer.initialize()

    def setup_project_structure(self) -> None:
        """Setup project structure."""
        log_info("Setting up project structure...")
        log_info("设置项目结构...", lang="zh")

        try:
            self.project_structure_setup.setup(self.project_name)
        except OSError as e:
            log_info(f"Warning: Failed to setup project structure: {e}")
            log_info(f"警告: 设置项目结构失败: {e}", lang="zh")

    def init_rust(self) -> None:
        """Initialize Rust environment."""
        log_info("Initializing Rust environment...")
        log_info("初始化Rust环境...", lang="zh")

        try:
            self.rust_initializer.initialize()
        except (OSError, subprocess.CalledProcessError) as e:
            log_info(f"Warning: Failed to initialize Rust environment: {e}")
            log_info(f"警告: 初始化Rust环境失败: {e}", lang="zh")

    def generate_pyproject(self) -> None:
        """Generate pyproject.toml if it doesn't exist."""
        if not Path("pyproject.toml").exists():
            log_info("pyproject.toml not found, generating...")
            log_info("未找到 pyproject.toml，正在生成...", lang="zh")

            try:
                # Create PyProjectGenerator instance and generate pyproject.toml
                generator = PyProjectGenerator(self.project_name)
                generator.set_project_info()
                generator.set_build_system(is_rust=Path("rust").exists())
                generator.set_development_tools()
                generator.generate()

                log_info("✓ pyproject.toml generated successfully")
                log_info("✓ pyproject.toml 生成成功", lang="zh")
            except (OSError, ValueError) as e:
                log_info(f"Warning: Failed to generate pyproject.toml: {e}")
                log_info(f"警告: 生成 pyproject.toml 失败: {e}", lang="zh")

    def sync_cargo_toml(self) -> None:
        """Sync Cargo.toml with pyproject.toml."""
        try:
            sync_toml_files(Path("pyproject.toml"), Path("rust/Cargo.toml"))
            log_info("✓ rust/Cargo.toml 已成功同步和更新。")
        except (OSError, ValueError) as e:
            log_info(f"Warning: Failed to sync Cargo.toml: {e}")
            log_info(f"警告: 同步 Cargo.toml 失败: {e}", lang="zh")

    def create_venv(self, is_windows: bool) -> None:
        """Create virtual environment."""
        if is_windows:
            self._create_venv_windows()
        else:
            self._create_venv_unix()

    def _detect_uv_workspace(self) -> bool:
        """Detect if we are in a uv workspace."""
        try:
            # Method 1: Check for explicit workspace configuration in pyproject.toml
            # This is the most reliable way to detect a workspace
            if self._check_pyproject_workspace():
                return True

            # Method 2: Check if uv init command indicates we're in a workspace
            if self._check_init_workspace():
                return True

            # Method 3: Check uv tree output for multiple root packages
            if self._check_tree_workspace():
                return True

            return False
        except (OSError, subprocess.SubprocessError) as e:
            return False

    def _check_init_workspace(self) -> bool:
        """Check if we are in a uv workspace by running uv init command."""
        try:
            import os
            import shutil
            from pathlib import Path

            # Create a temporary directory name for testing (valid Python package name)
            test_project_name = f"temp_uv_workspace_test_{os.getpid()}"

            # Run uv init to see if it detects a workspace
            result = subprocess.run(
                [sys.executable, "-m", "uv", "init", test_project_name],
                capture_output=True,
                text=True,
                env=self.env,
                encoding="utf-8",
                timeout=30,
            )

            # Clean up the test project directory if it was created
            test_project_path = Path(test_project_name)
            if test_project_path.exists():
                if test_project_path.is_dir():
                    shutil.rmtree(test_project_path)
                else:
                    test_project_path.unlink()

            # Check if the output indicates we are already in a workspace
            # The message can appear in either stdout or stderr
            output = result.stdout + result.stderr
            if "is already a member of workspace" in output:
                return True
            else:
                return False

        except (OSError, subprocess.SubprocessError, TimeoutError) as e:
            # Clean up in case of error
            import os
            from pathlib import Path

            test_project_name = f"temp_uv_workspace_test_{os.getpid()}"
            test_project_path = Path(test_project_name)
            if test_project_path.exists():
                if test_project_path.is_dir():
                    shutil.rmtree(test_project_path)
                else:
                    test_project_path.unlink()
            pass  # Ignore errors in workspace detection
        return False

    def _check_pyproject_workspace(self) -> bool:
        """Check if pyproject.toml contains workspace configuration."""
        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text(encoding="utf-8")
                # Look for workspace configuration in pyproject.toml
                if "[tool.uv.workspace]" in content or "tool.uv.workspace" in content:
                    return True
            except OSError as e:
                pass
        return False

    def _check_uv_lock_workspace(self) -> bool:
        """Check if uv.lock indicates a workspace."""
        uv_lock_path = Path("uv.lock")
        if uv_lock_path.exists():
            try:
                content = uv_lock_path.read_text(encoding="utf-8")
                # Count the number of package sections in the lock file
                package_count = content.count("[package]")

                # If there are multiple packages, it's likely a workspace
                # But we need to be careful - a regular project with many dependencies
                # could also have multiple packages in the lock file
                if package_count > 5:  # Arbitrary threshold, adjust as needed
                    # Let's also check if any package name matches the project name
                    # This would indicate it's the main package, not just a dependency
                    if self.project_name in content:
                        return False
                    else:
                        return True
            except OSError as e:
                pass
        return False

    def _check_tree_workspace(self) -> bool:
        """Check if uv tree indicates a workspace."""
        try:
            result = self._run_uv_tree_command()
            if not self._is_uv_tree_successful(result):
                return False

            root_packages = self._parse_uv_tree_output(result.stdout)

            # There should be more than one root package in a workspace
            if len(root_packages) > 1:
                return True
            elif len(root_packages) == 1:
                return self._determine_workspace_status(root_packages)
            else:
                return False
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return False
        except Exception as e:
            return False  # Ignore errors in workspace detection and return False

    def _run_uv_tree_command(self):
        """Run uv tree command with fallback to python -m uv."""
        # Method 3: Only run uv tree as a last resort since it's slow
        # We only need to run this if we haven't already determined workspace status
        # Try running uv directly first, fallback to python -m uv if that fails
        try:
            result = subprocess.run(
                ["uv", "tree"],
                capture_output=True,
                text=True,
                env=self.env,
                encoding="utf-8",
                timeout=30,  # Add timeout to prevent hanging
            )
        except (FileNotFoundError, OSError) as e:
            # If uv command not found, try python -m uv
            result = subprocess.run(
                [sys.executable, "-m", "uv", "tree"],
                capture_output=True,
                text=True,
                env=self.env,
                encoding="utf-8",
                timeout=30,  # Add timeout to prevent hanging
            )
        return result

    def _is_uv_tree_successful(self, result) -> bool:
        """Check if uv tree command was successful and has output."""
        # Check if the command succeeded
        if result.returncode != 0:
            return False

        # If no output, return False
        if not result.stdout.strip():
            return False

        return True

    def _parse_uv_tree_output(self, output: str) -> list:
        """Parse uv tree output to extract root packages."""
        lines = output.split("\n")
        root_packages = []
        for line in lines:
            stripped_line = line.rstrip()
            # Skip empty lines
            if not stripped_line or not stripped_line.strip():
                continue

            # Root package lines must not start with these prefixes
            skip_prefixes = [
                " ",
                "Resolved",
                "(*)",
                "├",
                "└",
                "│",
                "DEBUG",
                "Info:",
                "info:",
            ]
            if any(stripped_line.startswith(prefix) for prefix in skip_prefixes):
                continue

            # Skip lines that start with "v" (like "version v1.0.0")
            if stripped_line.strip().startswith("v"):
                continue

            # Check if this looks like a root package
            # Either with version: "package-name v1.2.3" or without version: "package-name"
            if " v" in stripped_line and not stripped_line.startswith("v"):
                # Package with version
                parts = stripped_line.split(" v", 1)
                if len(parts) == 2:
                    package_name = parts[0].strip()
                    version = parts[1].strip()
                    # Basic validation
                    if package_name and version:
                        root_packages.append(stripped_line)
            else:
                # Package without version - do additional checks
                # Skip lines with tree characters
                tree_chars = ["─", "┬", "├", "└", "│"]
                if not any(char in stripped_line for char in tree_chars):
                    # Add as root package if it passes all checks
                    if stripped_line.strip():
                        root_packages.append(stripped_line)

        return root_packages

    def _determine_workspace_status(self, root_packages: list) -> bool:
        """Determine workspace status based on root packages list."""
        # Updated logic for workspace detection:
        # 1. If we have multiple root packages, it's definitely a workspace
        # 2. If we have exactly one root package, check if it matches the project name
        #    - If it matches, we're in a regular project (not a workspace)
        #    - If it doesn't match, we might be in a workspace
        if len(root_packages) > 1:
            return True
        elif len(root_packages) == 1:
            # Extract the package name from the root package line
            root_package_line = root_packages[0]
            if " v" in root_package_line:
                root_package_name = root_package_line.split(" v")[0]
            else:
                root_package_name = root_package_line

            if root_package_name != self.project_name:
                return True
            else:
                return False
        else:
            return False

    def _create_venv_windows(self) -> None:
        """Create virtual environment on Windows."""
        # Check uv workspace status and create venv if needed
        log_info(
            "Checking uv workspace status to determine if virtual environment should be created..."
        )
        log_info("检查uv workspace状态以决定是否创建虚拟环境...", lang="zh")

        if self._detect_uv_workspace():
            log_info(
                "✓ uv workspace environment detected, skipping local .venv creation"
            )
            log_info("✓ 检测到uv workspace环境，跳过创建本地.venv", lang="zh")
        else:
            log_info("Ensuring virtual environment exists...")
            log_info("确保虚拟环境存在...", lang="zh")
            # Create virtual environment directly instead of calling external script
            venv_path = self.config_manager.get("venv_path", ".venv")
            python_version = self.config_manager.get("python_version", "3.10")
            if not self.venv_manager.create_venv_windows(venv_path, python_version):
                log_info("Warning: Failed to create virtual environment")
                log_info("警告: 创建虚拟环境失败", lang="zh")

    def _create_venv_unix(self) -> None:
        """Create virtual environment on Unix-like systems."""
        log_info(
            "Checking uv workspace status to determine if virtual environment should be created..."
        )
        log_info("检查uv workspace状态以决定是否创建虚拟环境...", lang="zh")

        if self._detect_uv_workspace():
            log_info(
                "✓ uv workspace environment detected, skipping local .venv creation"
            )
            log_info("✓ 检测到uv workspace环境，跳过创建本地.venv", lang="zh")
        else:
            log_info("Ensuring virtual environment exists...")
            log_info("确保虚拟环境存在...", lang="zh")
            venv_path = self.config_manager.get("venv_path", ".venv")
            python_version = self.config_manager.get("python_version", "3.10")
            if not self.venv_manager.create_venv_unix(
                venv_path, python_version, self.env
            ):
                log_info("Warning: Failed to create virtual environment")
                log_info("警告: 创建虚拟环境失败", lang="zh")
