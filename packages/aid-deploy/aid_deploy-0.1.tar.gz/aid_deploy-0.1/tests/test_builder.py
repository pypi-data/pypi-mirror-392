from pathlib import Path

from aid_deploy.builder import ComposeCmdBuilder


def test_add_argument_and_build() -> None:
    builder = ComposeCmdBuilder(command_template=["compose", "{args}", "zzz"])
    builder.add_argument("--project-name", "demo")
    builder.add_argument("-f", "/tmp/app.yaml")
    builder.add_argument("--env-file", "/tmp/.env")

    expected = [
        "compose",
        "--project-name",
        "demo",
        "-f",
        "/tmp/app.yaml",
        "--env-file",
        "/tmp/.env",
        "zzz",
    ]
    assert builder.build() == expected


def test_add_compose_folder_arguments(tmp_path: Path) -> None:
    # YAML
    (tmp_path / "b.yaml").write_text("version: '3'\n")
    (tmp_path / "a.yaml").write_text("version: '3'\n")
    (tmp_path / "z.yaml").write_text("version: '3'\n")

    (tmp_path / "fake.yaml").mkdir()  # dir will be ignored

    # YML
    (tmp_path / "c.yml").write_text("version: '3'\n")

    # Env
    (tmp_path / ".env").write_text("FOO=1\n")
    (tmp_path / ".env.local").write_text("BAR=2\n")
    (tmp_path / ".env-1").write_text("BAZ=3\n")

    (tmp_path / ".envdir").mkdir()  # dir will be ignored

    # Nested will be ignored
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "nested.yaml").write_text("version: '3'\n")
    (nested / ".env.nested").write_text("NESTED=1\n")

    builder = ComposeCmdBuilder(command_template=["compose", "{args}"])
    builder.add_compose_folder_arguments(tmp_path)

    def in_temp(name: str) -> str:
        return (tmp_path / name).as_posix()

    # yaml first, then env, each group sorted
    assert builder.args == [
        "-f",
        in_temp("a.yaml"),
        "-f",
        in_temp("b.yaml"),
        "-f",
        in_temp("z.yaml"),
        "-f",
        in_temp("c.yml"),
        "--env-file",
        in_temp(".env"),
        "--env-file",
        in_temp(".env-1"),
        "--env-file",
        in_temp(".env.local"),
    ]

    expected = [
        "compose",
        "-f",
        in_temp("a.yaml"),
        "-f",
        in_temp("b.yaml"),
        "-f",
        in_temp("z.yaml"),
        "-f",
        in_temp("c.yml"),
        "--env-file",
        in_temp(".env"),
        "--env-file",
        in_temp(".env-1"),
        "--env-file",
        in_temp(".env.local"),
    ]
    cmd = builder.build()
    assert cmd == expected


def test_add_compose_folder_arguments_empty_dir(tmp_path: Path) -> None:
    builder = ComposeCmdBuilder(command_template=["compose", "{args}", "zzz"])
    builder.add_compose_folder_arguments(tmp_path)

    assert builder.args == []
    assert builder.build() == ["compose", "zzz"]
