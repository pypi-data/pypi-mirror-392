"""
CLI main entry point for keynet-train.

This module provides the main() function that serves as the CLI entry point.
"""

import argparse
import logging
import sys

# Use shared login/logout from keynet-core
from keynet_core.cli.commands import handle_login as _core_login
from keynet_core.cli.commands import handle_logout as _core_logout

from .. import __version__
from .commands.push import setup_push_parser


def _setup_login_parser(subparsers: argparse._SubParsersAction) -> None:
    """Set up login parser with app-training path."""
    parser = subparsers.add_parser(
        "login",
        help="Login to keynet server",
        description="Authenticate with keynet server and store credentials",
    )
    parser.add_argument(
        "server_url",
        type=str,
        nargs="?",
        help="Server URL (e.g., https://api.example.com)",
    )
    parser.add_argument(
        "--username",
        type=str,
        help="Email address (will prompt if not provided)",
    )

    def handle_login_with_path(args: argparse.Namespace) -> int:
        """Wrapper to inject app-training path."""
        args.app_path = "app-training"
        return _core_login(args)

    parser.set_defaults(func=handle_login_with_path)


def _setup_logout_parser(subparsers: argparse._SubParsersAction) -> None:
    """Set up logout parser."""
    parser = subparsers.add_parser(
        "logout",
        help="Logout and clear credentials",
        description="Remove stored credentials from local configuration",
    )
    parser.set_defaults(func=_core_logout)


def main() -> int:
    """
    Main entry point for keynet-train CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)

    """
    # Suppress httpx INFO logs (e.g., "HTTP Request: GET ...")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(
        prog="keynet-train",
        description="Training utilities for keynet - Build and push container images with OCI artifacts",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"keynet-train {__version__}",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register commands
    _setup_login_parser(subparsers)
    _setup_logout_parser(subparsers)
    setup_push_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Execute command handler
    if hasattr(args, "func"):
        return args.func(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
