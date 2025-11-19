"""
Format code command."""

import argparse
import sys
from pathlib import Path

from ...commands import register_command
from ...commands.base import BaseCommand
from .python_formatter import (
    _run_format_command,
    format_examples,
    format_tools_scripts,
    format_with_python_tools,
    generate_type_stubs,
)
from .rust_formatter import format_rust_code


@register_command("format")
class FormatCommand(BaseCommand):
    """Command to format code."""

    @property
    def name(self) -> str:
        return "format"

    @property
    def help(self) -> str:
        return "Format code with ruff and cargo fmt"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "-q", "--quiet", action="store_true", help="Suppress detailed output"
        )
        parser.add_argument(
            "--unsafe", action="store_true", help="Enable ruff's unsafe fixes"
        )
        parser.add_argument(
            "--report",
            action="store_true",
            help="Generate format report in todos folder",
        )
        parser.add_argument(
            "paths",
            nargs="*",
            help="Paths to format (default: src, tools, examples, rust)",
        )

    def _format_specified_paths(self, paths, env, quiet, unsafe=False):
        """Format specified paths."""
        import os
        from pathlib import Path as PathClass

        from ...utils.logging import log_info

        for path in paths:
            # If path is already a Path-like object, use it directly
            # Otherwise, create a Path object from the string
            if (
                hasattr(path, "exists")
                and hasattr(path, "is_file")
                and hasattr(path, "is_dir")
                and hasattr(path, "name")
            ):
                path_obj = path
            else:
                path_obj = PathClass(path)

            if path_obj.exists():
                if path_obj.is_file() and path_obj.suffix == ".py":
                    # Format individual Python file with ruff only
                    try:
                        ruff_check_cmd = ["uv", "run", "ruff", "check", "--fix"]
                        if unsafe:
                            ruff_check_cmd.append("--unsafe-fixes")
                        ruff_check_cmd.append(str(path_obj))

                        _run_format_command(
                            ruff_check_cmd, env, quiet, passthrough=not quiet
                        )

                        # Also run ruff format for code formatting
                        _run_format_command(
                            [
                                "uv",
                                "run",
                                "ruff",
                                "format",
                                str(path_obj),
                            ],
                            env,
                            quiet,
                            passthrough=not quiet,
                        )
                    except Exception as e:
                        if not quiet:
                            print(f"Warning: Failed to format {path}: {e}")
                        # Re-raise to trigger sys.exit in execute method
                        raise
                elif path_obj.is_dir():
                    # Format directory with ruff only
                    # Special handling for rust directory - format both Python and Rust code
                    format_with_python_tools(str(path_obj), env, quiet, unsafe=unsafe)
                    if path_obj.name == "rust":
                        format_rust_code(str(path_obj), env, quiet)
            else:
                if not quiet:
                    print(f"Warning: Path {path} does not exist")

    def _format_python_directory(
        self, directory: str, env: dict, quiet: bool, unsafe: bool = False
    ) -> None:
        """Format Python directory with ruff only."""
        from pathlib import Path

        from ...utils.logging import log_info

        # Check if directory exists before attempting to format
        dir_path = Path(directory)
        if not dir_path.exists():
            if not quiet:
                print(f"Directory {directory} does not exist, skipping...")
            return

        format_with_python_tools(directory, env, quiet, unsafe)

    def _format_default_paths(self, project_root, env, quiet, unsafe=False):
        """Format default paths."""
        from pathlib import Path

        # Format source code with ruff only
        format_with_python_tools(str(project_root / "src"), env, quiet, unsafe)

        # Format tools scripts if directory exists
        tools_dir = project_root / "tools"
        if tools_dir.exists():
            format_with_python_tools(str(tools_dir), env, quiet, unsafe)

        # Format examples if directory exists
        examples_dir = project_root / "examples"
        if examples_dir.exists():
            format_with_python_tools(str(examples_dir), env, quiet, unsafe)

        # Generate type stubs
        generate_type_stubs(
            str(project_root / "src"), str(project_root / "typings"), env, quiet
        )

    def _find_project_root(self) -> Path:
        """
        Find the project root directory by looking for pyproject.toml file.
        通过查找 pyproject.toml 文件来确定项目根目录。
        """
        from py_wlcommands.utils.project_root import find_project_root

        return find_project_root()

    def _check_directory_with_ruff(
        self, directory: Path, project_root: Path
    ) -> tuple[str, str]:
        """Check a directory with ruff and return (stdout, stderr)."""
        import subprocess
        import sys

        try:
            ruff_check_result = subprocess.run(
                ["uv", "run", "ruff", "check", str(directory)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8" if sys.platform.startswith("win") else None,
            )
            return (ruff_check_result.stdout, ruff_check_result.stderr)
        except Exception as e:
            raise e

    def _write_report_for_directory(
        self, directory_name: str, stdout: str, stderr: str, report_lines: list
    ) -> bool:
        """Write report for a directory and return whether issues were found."""
        issues_found = False

        if stdout.strip():
            issues_found = True
            report_lines.append(f"## Issues in {directory_name}\n")
            report_lines.append("```\n")
            report_lines.append(stdout)
            report_lines.append("```\n")

        if stderr.strip():
            report_lines.append(f"## Errors in {directory_name}\n")
            report_lines.append("```\n")
            report_lines.append(stderr)
            report_lines.append("```\n")

        return issues_found

    def _generate_report(self, project_root: Path, quiet: bool) -> None:
        """Generate format report."""
        from pathlib import Path

        from ...utils.logging import log_info

        todos_dir = project_root / "todos"
        todos_dir.mkdir(exist_ok=True)

        # Run ruff check to get formatting issues only on the same paths as format command
        report_lines = ["# Format Report\n"]
        issues_found = False

        # Check directories in order: src, tools, examples
        directories_to_check = [
            ("src/", project_root / "src"),
            ("tools/", project_root / "tools"),
            ("examples/", project_root / "examples"),
        ]

        for dir_name, dir_path in directories_to_check:
            if dir_path.exists():
                try:
                    stdout, stderr = self._check_directory_with_ruff(
                        dir_path, project_root
                    )
                    if self._write_report_for_directory(
                        dir_name, stdout, stderr, report_lines
                    ):
                        issues_found = True
                except Exception as e:
                    if not quiet:
                        print(f"Warning: Failed to check {dir_name} directory: {e}")

        # If no issues found in any directory
        if not issues_found:
            report_lines.append("No format issues found.\n")

        # Write report to file
        report_file = todos_dir / "format_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.writelines(report_lines)

        if not quiet:
            log_info(f"Format report generated at {report_file}", lang="en")
            log_info(f"格式化报告已生成到 {report_file}", lang="zh")

    def execute(self, *args, **kwargs) -> None:
        """Execute the format command."""
        import os
        from pathlib import Path

        from ...utils.logging import log_error, log_info

        # Get arguments
        quiet = kwargs.get("quiet", False)
        unsafe = kwargs.get("unsafe", True)  # Default to True as per specifications
        report = kwargs.get("report", False)
        paths = kwargs.get("paths", [])

        # Handle --no-unsafe flag if present
        if "no_unsafe" in kwargs:
            unsafe = not kwargs["no_unsafe"]

        env = os.environ.copy()
        current_path = Path.cwd()

        # Handle report generation
        if report:
            self._generate_format_report(quiet, unsafe, paths, env)
            return

        try:
            # Format specified paths or default paths
            if paths:
                self._format_specified_paths(paths, env, quiet, unsafe)
            else:
                # Default behavior - format src, tools, examples, and rust directories
                src_path = current_path / "src"
                tools_path = current_path / "tools"
                examples_path = current_path / "examples"
                rust_path = current_path / "rust"

                # Format Python code
                if src_path.exists():
                    log_info("Formatting src directory...")
                    format_with_python_tools(str(src_path), env, quiet, unsafe=unsafe)

                if tools_path.exists():
                    log_info("Formatting tools directory...")
                    format_with_python_tools(str(tools_path), env, quiet, unsafe=unsafe)

                if examples_path.exists():
                    log_info("Formatting examples directory...")
                    format_with_python_tools(
                        str(examples_path), env, quiet, unsafe=unsafe
                    )

                # Generate type stubs
                typings_path = current_path / "typings"
                if src_path.exists() and typings_path.exists():
                    log_info("Generating type stubs...")
                    generate_type_stubs(str(src_path), str(typings_path), env, quiet)

                # Format Rust code
                if rust_path.exists():
                    log_info("Formatting Rust code...")
                    format_rust_code(str(rust_path), env, quiet)

            if not quiet:
                print("Formatting completed.")
        except Exception as e:
            if not quiet:
                print(f"Error occurred during formatting: {e}")
            sys.exit(1)

    def _generate_format_report(self, quiet, unsafe, paths, env):
        """Generate format report."""
        from pathlib import Path

        # Create todos directory if it doesn't exist
        todos_dir = Path("todos")
        todos_dir.mkdir(exist_ok=True)

        # Generate report content
        report_lines = []
        report_lines.append("# Format Report\n")
        report_lines.append("## Configuration\n")
        report_lines.append(f"- Quiet mode: {quiet}\n")
        report_lines.append(f"- Unsafe fixes: {unsafe}\n")
        report_lines.append(
            f"- Custom paths: {paths if paths else 'None (using defaults)'}\n"
        )

        # Save report
        report_path = todos_dir / "format_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        if not quiet:
            print(f"Format report generated at {report_path}")
