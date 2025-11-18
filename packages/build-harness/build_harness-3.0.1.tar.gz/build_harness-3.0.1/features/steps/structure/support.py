#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import contextlib
import os
import pathlib
import tempfile
import typing

import git

from build_harness._utility import run_command


@contextlib.contextmanager
def chdir_project_dir(
    path: pathlib.Path,
) -> typing.Generator[None, pathlib.Path, None]:
    current_dir = pathlib.Path(".").absolute()
    try:
        os.chdir(path)

        yield path
    finally:
        os.chdir(str(current_dir))


def create_venv(venv_path: pathlib.Path) -> pathlib.Path:
    result = run_command(
        ["python3", "-m", "venv", str(venv_path)],
        capture_output=True,
        universal_newlines=True,
    )
    assert result.returncode == 0

    pip_path = venv_path / "bin" / "pip"
    assert pip_path.is_file()

    return pip_path


def _install_working_build_harness(working_venvbin: pathlib.Path) -> None:
    result = run_command(
        [str(working_venvbin / "pip"), "install", "flit"],
        capture_output=True,
        universal_newlines=True,
    )
    print(result.stdout)
    print(result.stderr)

    assert result.returncode == 0

    result = run_command(
        [str(working_venvbin / "flit"), "install", "-s"],
        capture_output=True,
        universal_newlines=True,
    )
    print(result.stdout)
    print(result.stderr)

    assert result.returncode == 0

    assert (working_venvbin / "build-harness").is_file()


class MockTempDir:
    THIS_COUNT = 0
    name: str

    def __init__(self, debug_install: bool) -> None:
        self._debug_install = debug_install
        self._path = pathlib.Path(__file__).parent / "data/{0}".format(
            MockTempDir.THIS_COUNT
        )
        self._path.mkdir(exist_ok=True, parents=True)
        MockTempDir.THIS_COUNT += 1
        self.name = str(self._path)

    def cleanup(self) -> None:
        # Do nothing because this is for debug and in this case we want the
        # "temporary" workspace to persist for analysis.
        if not self._debug_install:
            self._path.rmdir()


@contextlib.contextmanager
def build_harness_context(
    create_pyproject: typing.Callable[[pathlib.Path], None],
    release_id: str,
    existing_project_venv: bool = False,
    debug_install: bool = False,
    pre_step_actions: typing.Optional[typing.Callable[[dict], None]] = None,
) -> typing.Generator[typing.Tuple[pathlib.Path, pathlib.Path], None, None]:
    temporary_dir = None
    try:
        if debug_install:
            temporary_dir = MockTempDir(debug_install)
        else:
            temporary_dir = tempfile.TemporaryDirectory()

        this_project = pathlib.Path(temporary_dir.name)
        working_venv = this_project / "working"
        working_venvbin = working_venv / "bin"

        if existing_project_venv:
            create_venv(this_project / ".venv")

        pyproject_path = this_project / "pyproject.toml"
        create_pyproject(pyproject_path)

        create_venv(working_venv)
        _install_working_build_harness(working_venvbin)

        work_build_harness = working_venvbin / "build-harness"

        if pre_step_actions:
            pre_step_actions(
                {"working_dir": this_project, "release_id": release_id}
            )

        yield (temporary_dir.name, work_build_harness)
    finally:
        if temporary_dir:
            temporary_dir.cleanup()


@contextlib.contextmanager
def git_repo_context(
    create_repo_commits: typing.Callable[[git.Repo], None],
    debug_install: bool = False,
    default_branch: str = "main",
) -> typing.Generator[typing.Tuple[pathlib.Path, pathlib.Path], None, None]:
    """
    Create a git repo context for a test.

    Args:
        create_repo_commits: Callable that creates a structure of commits in the repo
                             for a test.
        debug_install: Debug enabled creates the working directory locally and does
                       not erase it at the end of the test.
        default_branch: Default branch name for repo initialization.

    Yields:
        Tuple of paths to git repo directory and release-flow command respectively.
    """
    temporary_dir = None
    try:
        if debug_install:
            temporary_dir = MockTempDir(debug_install)
        else:
            temporary_dir = tempfile.TemporaryDirectory()

        working_dir = pathlib.Path(temporary_dir.name)
        working_venv = working_dir / ".venv"
        working_venvbin = working_venv / "bin"

        create_venv(working_venv)
        _install_working_build_harness(working_venvbin)

        r = git.Repo.init(str(working_dir), initial_branch=default_branch)
        create_repo_commits(r, working_dir)

        work_release_flow = working_venvbin / "release-flow"

        yield (working_dir, work_release_flow)
    finally:
        if temporary_dir:
            temporary_dir.cleanup()


def create_mock_pyproject(file_path: pathlib.Path) -> None:
    """Create a minimal flit based mock pyproject.toml file."""
    with file_path.open(mode="w") as f:
        f.write(
            """[build-system]
requires = ["flit_core >=2,<3"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
module = "some_module"
author = "Some Name"
author-email = "name@somewhere.com"
"""
        )


def create_source_dir(data: dict) -> None:
    """Create a mock project source directory."""
    working_dir = data["working_dir"]
    release_id = data["release_id"]
    source_dir = working_dir / "some_module"
    source_dir.mkdir(parents=True)
    init_file = source_dir / "__init__.py"
    with init_file.open(mode="w") as f:
        f.write('"""Just a mock project"""\n')
        f.write(
            """
__version__ = "{0}"
""".format(
                release_id
            )
        )
