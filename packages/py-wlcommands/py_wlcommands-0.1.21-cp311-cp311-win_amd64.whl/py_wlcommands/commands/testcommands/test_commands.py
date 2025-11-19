"""
Test command implementation for wl tool.
"""

import os
import subprocess
import sys
from typing import Any

from .. import register_command
from ..base import BaseCommand


@register_command("test")
class TestCommand(BaseCommand):
    """Command to run tests for the project."""

    # Tell pytest not to collect this class as a test class
    __test__ = False

    @property
    def name(self) -> str:
        """Get the command name."""
        return "test"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Run project tests"

    def add_arguments(self, parser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--report",
            action="store_true",
            help="Show detailed test report including verbose output and coverage",
        )

    def _build_command_args(self, report_mode: bool, args) -> list[str]:
        """Build the command arguments for pytest."""
        cmd_args: list[str] = [sys.executable, "-m", "pytest"]

        # Add verbose flag only in report mode
        if report_mode:
            cmd_args.append("-v")
            cmd_args.append("--tb=short")  # Show shorter tracebacks for failures
        else:
            # Default mode - same as python -m pytest --tb=no -q --no-header
            cmd_args.append("--tb=no")  # Don't show tracebacks
            cmd_args.append("-q")  # Quiet mode
            cmd_args.append("--no-header")  # Don't show pytest header

        # Parse args to check if user provided their own --cov option
        has_user_cov = any(arg.startswith("--cov") for arg in args)

        # Only add default coverage if no user-defined cov and plugin is available
        if not has_user_cov and report_mode:
            has_pytest_cov = self._check_pytest_cov()
            if has_pytest_cov:
                cmd_args.extend(["--cov=py_wlcommands", "--cov-report=term-missing"])

        # Add any additional user arguments
        if args:
            # Check if any argument looks like a test file/directory path (doesn't start with --)
            has_path_arg = any(not arg.startswith("--") for arg in args)
            cmd_args.extend(args)

            # Only add default test path if not in report mode and no path arguments provided
            if not report_mode and not has_path_arg:
                cmd_args.append("tests/")
        else:
            # If no args provided, add default test path
            cmd_args.append("tests/")

        return cmd_args

    def _handle_test_result(self, result, report_mode: bool) -> None:
        """
        Handle the test result based on return code.

        Args:
            result: The subprocess result object
            report_mode: Whether we're in report mode
        """
        if result.returncode == 0:
            # Tests passed
            if not report_mode:
                print("All tests passed successfully!")
        else:
            # Tests failed
            if not report_mode:
                # In quiet mode, show the output when tests fail
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
                print(f"Tests failed with return code {result.returncode}")
            sys.exit(result.returncode)

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """
        Execute the test command.

        Args:
            *args: Positional arguments (can include pytest arguments like --cov)
            **kwargs: Keyword arguments
        """
        # Check if report mode is enabled
        report_mode = kwargs.get("report", False)

        # Run pytest to execute tests
        try:
            cmd_args = self._build_command_args(report_mode, args)

            if report_mode:
                # In report mode, pass through stdout/stderr to preserve colors and formatting
                result = subprocess.run(
                    cmd_args,
                    cwd=self._get_project_root(),
                    check=False,
                )
            else:
                # In quiet mode, also pass through stdout/stderr to preserve colors and formatting
                result = subprocess.run(
                    cmd_args,
                    cwd=self._get_project_root(),
                    check=False,
                )

            # Handle the test result
            self._handle_test_result(result, report_mode)

        except FileNotFoundError:
            print(
                "Error: pytest not found. Please install it using 'pip install pytest'"
            )
            sys.exit(1)
        except Exception as e:
            print(f"Error running tests: {e}")
            sys.exit(1)

    def _check_pytest_cov(self) -> bool:
        """
        Check if pytest-cov plugin is available.

        Returns:
            bool: True if pytest-cov is available, False otherwise
        """
        try:
            import pytest_cov

            return True
        except ImportError:
            return False

    def _get_project_root(self) -> str:
        """
        Get the project root directory.

        Returns:
            str: Path to the project root directory
        """
        # For now, assume the project root is the current working directory
        return os.getcwd()
