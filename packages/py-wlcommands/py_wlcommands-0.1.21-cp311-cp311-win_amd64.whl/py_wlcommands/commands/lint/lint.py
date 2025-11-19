"""
Lint command.
"""

import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

from py_wlcommands.commands import Command, register_command, validate_command_args
from py_wlcommands.commands.format.format_command import FormatCommand
from py_wlcommands.utils.logging import log_info


@register_command("lint")
class LintCommand(Command):
    """Command to lint code."""

    @property
    def name(self) -> str:
        return "lint"

    @property
    def help(self) -> str:
        return "Lint code with ruff - equivalent to make lint"

    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "paths", nargs="*", help="Paths to lint (default: current directory)"
        )
        parser.add_argument(
            "-q", "--quiet", action="store_true", help="Suppress detailed output"
        )
        parser.add_argument(
            "--fix", action="store_true", help="Automatically fix lint errors"
        )
        parser.add_argument(
            "--noreport",
            action="store_true",
            help="Do not generate lint report in todos folder",
        )

    @validate_command_args()
    def execute(
        self,
        paths: list[str] | None = None,
        quiet: bool = False,
        fix: bool = False,
        noreport: bool = False,
        **kwargs: dict[str, object],
    ) -> None:
        """
        Lint code - equivalent to make lint
        代码静态检查 - 等效于 make lint
        """
        # 忽略传递的额外参数，例如'command'
        # Ignore extra arguments passed, such as 'command'

        if not quiet:
            self._log_info("Linting code...", "正在进行代码静态检查...")

        try:
            # Get project root directory
            project_root = self._get_project_root()

            # First, format the code
            # 首先，格式化代码
            self._format_code(project_root, paths, quiet)

            # Prepare and run ruff command
            cmd = self._prepare_ruff_command(paths, fix, quiet)

            # Execute ruff command
            result = self._run_ruff_command(cmd, project_root, quiet, noreport)

            # Generate report if requested (default behavior)
            if not noreport:
                self._generate_report(result, project_root, quiet)

            # Handle result
            self._handle_result(result, quiet)

            # 如果有错误，退出码非0
            if result.returncode != 0:
                sys.exit(result.returncode)

        except FileNotFoundError:
            self._handle_file_not_found_error(quiet)
            sys.exit(1)
        except Exception as e:
            self._handle_general_error(e, quiet)
            sys.exit(1)

    def _get_project_root(self) -> Path:
        """Get the project root directory by looking for pyproject.toml file."""
        from py_wlcommands.utils.project_root import find_project_root

        return find_project_root()

    def _log_info(self, en_msg: str, zh_msg: str) -> None:
        """Log info message in both English and Chinese."""
        log_info(en_msg, lang="en")
        log_info(zh_msg, lang="zh")

    def _format_code(
        self, project_root: Path, paths: list[str] | None, quiet: bool
    ) -> None:
        """Format code before linting."""
        if not quiet:
            self._log_info(
                "Formatting code before linting...", "在静态检查前先格式化代码..."
            )

        format_cmd = FormatCommand()
        # Pass the unsafe=True parameter to match the default behavior of the format command
        format_cmd.execute(quiet=quiet, unsafe=True, paths=paths)

    def _prepare_ruff_command(
        self, paths: list[str] | None, fix: bool, quiet: bool
    ) -> list[str]:
        """Prepare the ruff command."""
        # Prepare ruff command
        cmd = ["ruff", "check"]

        # Add paths to lint or default to current directory
        if paths:
            cmd.extend(paths)
        else:
            cmd.append(".")

        # Add fix flag if requested
        if fix:
            cmd.append("--fix")

        # Add quiet flag if requested
        if quiet:
            cmd.append("--quiet")

        return cmd

    def _run_ruff_command(
        self, cmd: list[str], project_root: Path, quiet: bool, noreport: bool
    ) -> subprocess.CompletedProcess:
        """Run the ruff command and return the result."""
        # Execute ruff command
        # 在 subprocess.run 调用中忽略 S603 警告，因为我们执行的是受信任的命令
        if quiet or not noreport:
            # In quiet mode, capture output to suppress it
            result = subprocess.run(  # nosec B603
                cmd,
                cwd=str(project_root),
                capture_output=True,
                text=True,
                # Explicitly set encoding for Windows systems
                encoding="utf-8" if sys.platform.startswith("win") else None,
            )
        else:
            # In normal mode, let ruff output directly to stdout/stderr to preserve colors
            result = subprocess.run(
                cmd,
                cwd=str(project_root),
                # Explicitly set encoding for Windows systems
                encoding="utf-8" if sys.platform.startswith("win") else None,
            )  # nosec B603

        return result

    def _generate_report(
        self, result: subprocess.CompletedProcess, project_root: Path, quiet: bool
    ) -> None:
        """Generate lint report."""
        todos_dir = project_root / "todos"
        todos_dir.mkdir(exist_ok=True)

        report_file = todos_dir / "lint_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# Lint Report\n\n")
            if result.stdout:
                f.write("## Issues Found\n\n")
                f.write("```\n")
                f.write(result.stdout)
                f.write("```\n")
            else:
                f.write("No lint issues found.\n")

            if result.stderr:
                f.write("\n## Errors\n\n")
                f.write("```\n")
                f.write(result.stderr)
                f.write("```\n")

        if not quiet:
            self._log_info(
                f"Lint report generated at {report_file}",
                f"静态检查报告已生成到 {report_file}",
            )

    def _handle_result(self, result: subprocess.CompletedProcess, quiet: bool) -> None:
        """Handle the result of the linting process."""
        if result.returncode != 0 and not quiet:
            self._log_info(
                "Linting completed with issues:", "代码静态检查发现以下问题:"
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        elif result.returncode == 0 and not quiet:
            self._log_info(
                "Code linting completed successfully!", "代码静态检查成功完成！"
            )

    def _handle_file_not_found_error(self, quiet: bool) -> None:
        """Handle FileNotFoundError."""
        if not quiet:
            self._log_info(
                "Error: ruff is not installed or not found in PATH",
                "错误：未安装 ruff 或在 PATH 中找不到",
            )

    def _handle_general_error(self, e: Exception, quiet: bool) -> None:
        """Handle general exceptions."""
        if not quiet:
            self._log_info(f"Error during linting: {e}", f"错误：静态检查期间出错: {e}")
