#!/usr/bin/env python3
"""Deploy an app to a node"""

import argparse
from pathlib import Path
from typing import Callable, Protocol

from .builder import ComposeCmdBuilder
from .instance import Instance
from .scanner import FolderScanner


class ComposeExecutor(Protocol):
    """An executor for a docker compose command"""

    def up(self) -> None:
        """Up the instance"""

    def down(self) -> None:
        """Down the instance"""

    def deploy(self) -> None:
        """Deploy the instance"""


InstanceCommandFn = Callable[[ComposeExecutor], None]

VALID_COMMANDS: dict[str, InstanceCommandFn] = {
    "deploy": lambda executor: executor.deploy(),
    "down": lambda executor: executor.down(),
    "up": lambda executor: executor.up(),
}


def main():
    """Main entry point"""

    args = parse_arguments(
        argparse.ArgumentParser(
            description="Deploy an app to a node",
            epilog="Example: deploy.py ./path/to/app",
        )
    )

    app_path = Path(args.source).resolve()

    if not app_path.exists():
        raise FileNotFoundError(f"App {app_path} not found")

    print(f"Running `{args.command}` in `{args.source}`")
    run_app_command(app_path, args.command, args.verbose, args.dry_run)


def parse_arguments(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Parse the command line arguments"""

    parser.add_argument(
        "source",
        type=str,
        help="Path to the app configuration directory",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Dry run",
    )
    parser.add_argument(
        "-c",
        "--command",
        choices=tuple(VALID_COMMANDS.keys()),
        default="deploy",
        help="Command to run",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    return parser.parse_args()


def run_app_command(app_path: Path, command: str, verbose: bool, dry_run: bool) -> None:
    """Run a command for all instances of an app"""

    for instance_conf_dirs in FolderScanner(app_path).scan():
        instance = Instance(instance_conf_dirs, ComposeCmdBuilder)
        instance.set_verbose(verbose)
        instance.set_dry_run(dry_run)
        run_instance_command(instance, command)


def run_instance_command(instance: Instance, command: str) -> None:
    """Run a command for an instance of a service"""

    verbs = {"deploy": "Deploying", "up": "Bringing up", "down": "Bringing down"}
    print(f"[{instance.id}] {verbs.get(command, command.capitalize())} instance")

    VALID_COMMANDS[command](instance)

    print(f"[{instance.id}] Done")


if __name__ == "__main__":
    main()
