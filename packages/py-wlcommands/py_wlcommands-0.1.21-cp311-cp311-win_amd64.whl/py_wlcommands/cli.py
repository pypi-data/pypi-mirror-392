#!/usr/bin/env python3
"""Command line interface entry point."""

import argparse
import sys

from .utils.error_handler import ErrorHandler
from .utils.logging import log_error

logger = None  # Using the simple log_error function instead


def main(argv: list[str] = None) -> int:
    """Main entry point for the CLI."""
    if argv is None:
        argv = sys.argv[1:]

    from .commands import get_command, list_commands

    commands = list_commands()

    def get_command_help(command_class):
        """Get help text from command class."""
        try:
            # Create instance and get help property value
            instance = command_class()
            return instance.help
        except (AttributeError, TypeError):
            # Fallback to class name if help property fails
            return "No help available"

    parser = argparse.ArgumentParser(
        prog="wl",
        description="A command-line tool for project management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
"""
        + "\n".join(
            [f"  {name:<12} {get_command_help(cls)}" for name, cls in commands.items()]
        ),
    )

    # Add subparsers for each command
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register each command's arguments
    for name, command_class in commands.items():
        # Create instance to get help text
        command_instance = command_class()
        subparser = subparsers.add_parser(name, help=command_instance.help)
        if hasattr(command_instance, "add_arguments"):
            command_instance.add_arguments(subparser)

    # Parse arguments
    args, unknown_args = parser.parse_known_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Find and execute the command
    try:
        command_instance = get_command(args.command)
    except ValueError as e:
        log_error(str(e))
        return 1

    # Combine known and unknown args
    kwargs = vars(args)
    command_name = kwargs.pop("command", None)

    # Add unknown args to kwargs for the command to handle
    if unknown_args:
        kwargs["unknown_args"] = unknown_args

    try:
        # Use error handler to wrap command execution
        ErrorHandler.wrap_command_execution(command_instance.execute, **kwargs)
        return 0
    except Exception as e:
        log_error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
