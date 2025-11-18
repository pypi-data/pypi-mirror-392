"""An instance of a service"""

import subprocess
from pathlib import Path
from typing import Callable, Protocol

COMPOSE_UP_TEMPLATE = ["docker", "compose", "{args}", "up", "-d"]
COMPOSE_DOWN_TEMPLATE = ["docker", "compose", "{args}", "down", "--remove-orphans"]

ConfDirs = tuple[Path, ...]


class CmdBuilder(Protocol):
    """A command builder"""

    def add_argument(self, name: str, value: str) -> None:
        """Add an argument to the command"""
        ...  # pylint: disable=unnecessary-ellipsis

    def add_compose_folder_arguments(self, folder: Path) -> None:
        """Add a compose folder to the command arguments"""
        ...  # pylint: disable=unnecessary-ellipsis

    def build(self) -> list[str]:
        """Build the command"""
        ...  # pylint: disable=unnecessary-ellipsis


class Instance:
    """An instance of a service"""

    def __init__(
        self, dirs: ConfDirs, cmd_builder_factory: Callable[[list[str]], CmdBuilder]
    ):
        self.config_dirs: ConfDirs = dirs
        self._builder: CmdBuilder | None = None
        self._cmd_builder_factory = cmd_builder_factory

        self._verbose = False
        self._dry_run = False

        self.id = self._infer_id(dirs)

    def set_verbose(self, verbose: bool) -> None:
        """Set the verbose flag"""

        self._verbose = verbose

    def set_dry_run(self, dry_run: bool) -> None:
        """Set the dry run flag"""

        self._dry_run = dry_run

    def _infer_id(self, dirs: ConfDirs) -> str:
        """Infer the service id from the configuration directories"""

        return "-".join(folder.name for folder in dirs)

    def build_compose_cmd(self, template: list[str]) -> list[str]:
        """Build a docker compose command"""

        self._builder = self._cmd_builder_factory(template)
        self._builder.add_argument("--project-name", self.id)

        for config_dir in self.config_dirs:
            self._builder.add_compose_folder_arguments(config_dir)

        return self._builder.build()

    def down(self) -> None:
        """Down the instance"""

        cmd = self.build_compose_cmd(COMPOSE_DOWN_TEMPLATE)
        self._run(cmd, check=False)

    def up(self) -> None:
        """Up the instance"""

        cmd = self.build_compose_cmd(COMPOSE_UP_TEMPLATE)
        self._run(cmd)

    def deploy(self) -> None:
        """Deploy the instance"""

        self.down()
        self.up()

    def _run(self, cmd: list[str], check: bool = True) -> None:
        """Run a command"""

        if self._verbose:
            print(f"[{self.id}] {' '.join(cmd)}")

        if self._dry_run:
            return

        subprocess.run(cmd, check=check)
