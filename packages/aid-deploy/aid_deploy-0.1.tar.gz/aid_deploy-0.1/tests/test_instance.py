from pathlib import Path
from typing import Iterable, List, Tuple

from aid_deploy.instance import (
    COMPOSE_DOWN_TEMPLATE,
    COMPOSE_UP_TEMPLATE,
    Instance,
)

TEMPLATE = ["custom", "{args}", "zzz"]


class MockCmdBuilder:
    def __init__(self, template: list[str]):
        self.template = template
        self.arguments: List[Tuple[str, str]] = []
        self.folders: List[Path] = []

    def add_argument(self, name: str, value: str) -> None:
        self.arguments.append((name, value))

    def add_compose_folder_arguments(self, folder: Path) -> None:
        self.folders.append(folder)

    def build(self) -> list[str]:
        ans: list[str] = []
        idx = self.template.index("{args}")
        ans.extend(self.template[:idx])
        for name, value in self.arguments:
            ans.extend([name, value])
        ans.extend(self.template[idx + 1 :])
        return ans


def expand_args_template(template: list[str], args: Iterable[str]) -> list[str]:
    PATTERN = "{args}"

    result: list[str] = []

    idx = template.index(PATTERN)
    result.extend(template[:idx])
    result.extend(args)
    result.extend(template[idx + 1 :])

    return result


def test_build_compose_cmd(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"

    instance = Instance((a, b), MockCmdBuilder)
    cmd = instance.build_compose_cmd(TEMPLATE)
    expected = expand_args_template(TEMPLATE, ("--project-name", "a-b"))

    assert cmd == expected
    assert instance._builder is not None  # pylint: disable=protected-access
    assert instance._builder.arguments == [("--project-name", "a-b")]  # type: ignore # pylint: disable=protected-access
    assert instance._builder.folders == [a, b]  # type: ignore # pylint: disable=protected-access


def test_up_down(tmp_path: Path) -> None:
    root = tmp_path / "root"
    instance = Instance((root,), MockCmdBuilder)
    calls: List[Tuple[list[str], bool]] = []

    def capture_run(cmd: list[str], check: bool = True) -> None:
        calls.append((cmd, check))

    instance._run = capture_run  # pylint: disable=protected-access

    instance.down()
    instance.up()

    print(calls)
    expected = [
        (
            expand_args_template(COMPOSE_DOWN_TEMPLATE, ("--project-name", "root")),
            False,
        ),
        (
            expand_args_template(COMPOSE_UP_TEMPLATE, ("--project-name", "root")),
            True,
        ),
    ]
    assert calls == expected


def test_run(monkeypatch, tmp_path: Path) -> None:
    d = tmp_path / "d"

    class SimpleBuilder(MockCmdBuilder):
        def build(self) -> list[str]:
            return ["exec-me"]

    instance = Instance((d,), SimpleBuilder)
    instance.set_verbose(False)
    instance.set_dry_run(False)

    calls: List[Tuple[list[str], bool]] = []

    def capture_run(cmd: list[str], check: bool = True) -> None:
        calls.append((cmd, check))

    import subprocess as _subprocess  # patch target

    monkeypatch.setattr(_subprocess, "run", capture_run)

    instance.up()
    instance.down()

    assert calls == [
        (["exec-me"], True),
        (["exec-me"], False),
    ]
