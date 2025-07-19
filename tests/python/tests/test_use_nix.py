import logging
import os
import shlex
import subprocess
import sys
import unittest

import pytest

from .direnv_project import DirenvProject
from .procs import run

log = logging.getLogger(__name__)


def direnv_exec(
    direnv_project: DirenvProject, cmd: str, env: dict[str, str] | None = None
) -> None:
    args = ["direnv", "exec", str(direnv_project.directory), "sh", "-c", cmd]
    log.debug(f"$ {shlex.join(args)}")
    out = run(
        args,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        check=False,
        cwd=direnv_project.directory,
        env=env,
    )
    sys.stdout.write(out.stdout)
    sys.stderr.write(out.stderr)
    assert out.returncode == 0
    assert out.stdout == "OK\n"
    assert "Renewed cache" in out.stderr


@pytest.mark.parametrize("strict_env", [False, True])
def test_attrs(direnv_project: DirenvProject, strict_env: bool) -> None:
    direnv_project.setup_envrc("use nix -A subshell", strict_env=strict_env)
    direnv_exec(direnv_project, "echo $THIS_IS_A_SUBSHELL")


@pytest.mark.parametrize("strict_env", [False, True])
def test_no_nix_path(direnv_project: DirenvProject, strict_env: bool) -> None:
    direnv_project.setup_envrc("use nix --argstr someArg OK", strict_env=strict_env)
    env = os.environ.copy()
    del env["NIX_PATH"]
    direnv_exec(direnv_project, "echo $SHOULD_BE_SET", env=env)


@pytest.mark.parametrize("strict_env", [False, True])
def test_args(direnv_project: DirenvProject, strict_env: bool) -> None:
    direnv_project.setup_envrc("use nix --argstr someArg OK", strict_env=strict_env)
    direnv_exec(direnv_project, "echo $SHOULD_BE_SET")


@pytest.mark.parametrize("strict_env", [False, True])
def test_no_files(direnv_project: DirenvProject, strict_env: bool) -> None:
    direnv_project.setup_envrc("use nix -p hello", strict_env=strict_env)
    out = run(
        ["direnv", "status"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        check=False,
        cwd=direnv_project.directory,
    )
    assert out.returncode == 0
    assert 'Loaded watch: "."' not in out.stdout


if __name__ == "__main__":
    unittest.main()
