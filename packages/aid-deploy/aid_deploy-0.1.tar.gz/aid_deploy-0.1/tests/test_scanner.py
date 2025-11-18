from pathlib import Path
from typing import Iterable, Iterator

from aid_deploy.instance import ConfDirs
from aid_deploy.scanner import FolderScanner


def _as_str_tuples(it: Iterable[ConfDirs]) -> set[tuple[str, ...]]:
    return {tuple(p.as_posix() for p in t) for t in it}


def test_scan_single_empty_root(tmp_path: Path) -> None:
    leaves: Iterator[ConfDirs] = FolderScanner(tmp_path).scan()
    assert list(leaves) == [(tmp_path,)]


def test_scan_multiple_nested_leaves(tmp_path: Path) -> None:
    (tmp_path / "a" / "x").mkdir(parents=True)
    (tmp_path / "a" / "y").mkdir(parents=True)
    (tmp_path / "a" / "file.txt").write_text("ignored")

    (tmp_path / "b" / "z" / "u").mkdir(parents=True)
    (tmp_path / "b" / "z" / "v").mkdir(parents=True)
    (tmp_path / "b" / "zfile.txt").write_text("ignored")

    leaves: Iterator[ConfDirs] = FolderScanner(tmp_path).scan()

    expected = {
        (
            tmp_path.as_posix(),
            (tmp_path / "a").as_posix(),
            (tmp_path / "a" / "x").as_posix(),
        ),
        (
            tmp_path.as_posix(),
            (tmp_path / "a").as_posix(),
            (tmp_path / "a" / "y").as_posix(),
        ),
        (
            tmp_path.as_posix(),
            (tmp_path / "b").as_posix(),
            (tmp_path / "b" / "z").as_posix(),
            (tmp_path / "b" / "z" / "u").as_posix(),
        ),
        (
            tmp_path.as_posix(),
            (tmp_path / "b").as_posix(),
            (tmp_path / "b" / "z").as_posix(),
            (tmp_path / "b" / "z" / "v").as_posix(),
        ),
    }

    assert _as_str_tuples(leaves) == expected


def test_scan_yields_only_deepest_dirs(tmp_path: Path) -> None:
    (tmp_path / "top.txt").write_text("ignored")
    (tmp_path / "a" / "child").mkdir(parents=True)
    (tmp_path / "a" / "file.txt").write_text("ignored")
    (tmp_path / "a" / "child" / "file.txt").write_text("ignored")

    leaves: Iterator[ConfDirs] = FolderScanner(tmp_path).scan()

    expected = {
        (
            tmp_path.as_posix(),
            (tmp_path / "a").as_posix(),
            (tmp_path / "a" / "child").as_posix(),
        )
    }
    assert _as_str_tuples(leaves) == expected
