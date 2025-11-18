"""Build a docker compose command"""

from pathlib import Path


class ComposeCmdBuilder:
    """Build a docker compose command"""

    def __init__(self, command_template: list[str]):
        self.command_template: list[str] = command_template
        self.args: list[str] = []

    def add_compose_folder_arguments(self, folder: Path) -> None:
        """Add all yaml and env files in a folder to the command"""

        self.add_glob_files_args(folder, "-f", "*.yaml")
        self.add_glob_files_args(folder, "-f", "*.yml")
        self.add_glob_files_args(folder, "--env-file", ".env*")

    def add_glob_files_args(self, folder: Path, arg_name: str, mask: str) -> None:
        """Add all files in a folder to the command"""

        for file in sorted(folder.glob(mask)):
            if not file.is_file():
                continue
            self.add_argument(arg_name, file.as_posix())

    def add_argument(self, name: str, value: str) -> None:
        """Add an argument to the command"""

        self.args.extend([name, value])

    def build(self) -> list[str]:
        """Build the command"""

        cmd: list[str] = []
        for token in self.command_template:
            if token == "{args}":
                cmd.extend(self.args)
            else:
                cmd.append(token)
        return cmd
