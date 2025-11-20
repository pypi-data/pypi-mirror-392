"""
Main CLI entry point for keynet.

This module provides the unified keynet CLI with common commands
shared across train and inference packages.
"""

import argparse
import sys

from .commands import setup_login_parser, setup_logout_parser


def main() -> int:
    """
    Main entry point for keynet CLI.

    Returns:
        Exit code (0 for success, non-zero for error)

    """
    parser = argparse.ArgumentParser(
        prog="keynet",
        description="Keynet CLI - Common commands for authentication and configuration",
        epilog="""
For train-specific commands, use: keynet-train
For inference-specific commands, use: keynet-inference

Examples:
    keynet login https://api.example.com
    keynet logout
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.7.4",
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Register commands
    setup_login_parser(subparsers)
    setup_logout_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    try:
        return args.func(args)
    except AttributeError:
        parser.print_help()
        return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())
