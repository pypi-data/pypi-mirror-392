"""Scan a folder for instance configurations"""

from pathlib import Path
from typing import Iterator

from .instance import ConfDirs


class FolderScanner:
    """Scan a folder for instance configurations"""

    def __init__(self, folder: Path):
        self.folder: Path = folder

    def scan(self) -> Iterator[ConfDirs]:
        """Yields tuples of instance configuration directories"""

        yield from self._gather_deepest(self.folder, ())

    def _gather_deepest(self, path: Path, dirs: ConfDirs) -> Iterator[ConfDirs]:
        """Gather deepest instance configuration directories recursively"""

        new_dirs = (*dirs, path)

        has_subfolders = False

        for subpath in path.iterdir():
            if not subpath.is_dir():
                continue
            yield from self._gather_deepest(subpath, new_dirs)
            has_subfolders = True

        if not has_subfolders:
            yield new_dirs
