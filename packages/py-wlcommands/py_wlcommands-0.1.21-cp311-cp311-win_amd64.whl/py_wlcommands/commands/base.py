"""Base command class for WL Commands."""

import argparse
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseCommand(ABC):
    """
    Abstract base class for all commands.

    All command classes should inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self, **dependencies: Any) -> None:
        """
        Initialize the command with dependencies.

        Args:
            **dependencies: Dependencies to inject into the command
        """
        self._dependencies = dependencies

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the command name.

        Returns:
            str: The command name
        """
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """
        Get the command help text.

        Returns:
            str: The command help text
        """
        pass

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser to add arguments to
        """
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """
        Execute the command.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        pass

    def validate_args(self, **kwargs: Any) -> dict[str, Any]:
        """
        Validate command arguments.

        Args:
            **kwargs: Arguments to validate

        Returns:
            Dict[str, Any]: Validated arguments

        Raises:
            ValueError: If arguments are invalid
        """
        return kwargs

    def handle_error(self, error: Exception) -> None:
        """
        Handle errors that occur during command execution.

        Args:
            error (Exception): The error that occurred
        """
        raise error
