#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import copy
import pathlib
import subprocess
import typing

import pytest

from build_harness.commands import main
from build_harness.commands.dependencies import (
    DependencyCheckError,
    DependencyInstallError,
    ExitState,
    ProjectDependencies,
    PyprojecttomlError,
    VenvError,
    VenvPipError,
    _check_dependencies,
    _check_dependency_names,
    _check_virtual_environment,
    _extract_pip_list_packages,
    _install_all_project_dependencies,
    _install_project_dependencies,
)
from tests.ci.support.click_runner import click_runner  # noqa: F401

MOCK_VENV_BIN_PATH = pathlib.Path("some/test_dependencies/bin")


class TestExtractPipListPackages:
    sample_output = """
Package                       Version
----------------------------- ---------
alabaster                     0.7.12
black                         20.8b1
certifi                       2020.6.20
"""

    def test_clean(self):
        result = _extract_pip_list_packages(self.sample_output)

        assert result == [
            ("alabaster", "0.7.12"),
            ("black", "20.8b1"),
            ("certifi", "2020.6.20"),
        ]

    def test_empty(self):
        sample_output = """"""

        result = _extract_pip_list_packages(sample_output)

        assert result == list()

    def test_empty_list(self):
        sample_output = """
Package                       Version
----------------------------- ---------
"""

        result = _extract_pip_list_packages(sample_output)

        assert result == list()


class TestCheckDependencies:
    def test_clean(self, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """
Package                       Version
----------------------------- ---------
pkg1                     0.7.12
pkg_name2                         20.8b1
pkg3                       2020.6.20
"""
        mock_dependencies = ProjectDependencies(
            runtime=["pkg-name2==20.8b1"], dev=list(), doc=list(), test=list()
        )

        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )

        _check_dependencies(MOCK_VENV_BIN_PATH, mock_dependencies, "all")

    def test_empty_venv_dependencies(self, mocker):
        """Empty venv with project dependencies fails."""
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """
Package                       Version
----------------------------- ---------
"""
        mock_dependencies = ProjectDependencies(
            runtime=["pkg2==20.8b1"], dev=list(), doc=list(), test=list()
        )

        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )

        with pytest.raises(
            DependencyCheckError,
            match=r"^Project dependencies not installed",
        ):
            _check_dependencies(MOCK_VENV_BIN_PATH, mock_dependencies, "all")

    def test_bad_specifier(self, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """
Package                       Version
----------------------------- ---------
pkg1                     0.7.12
pkg2                         20.8b1
pkg3                       2020.6.20
"""
        mock_dependencies = ProjectDependencies(
            runtime=["pkg2==19.0"], dev=list(), doc=list(), test=list()
        )

        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )

        with pytest.raises(
            DependencyCheckError,
            match=r"^Installed packages do not comply with declared project dependencies",
        ):
            _check_dependencies(MOCK_VENV_BIN_PATH, mock_dependencies, "all")

    def test_missing_package(self, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """
Package                       Version
----------------------------- ---------
pkg1                     0.7.12
pkg2                         20.8b1
pkg3                       2020.6.20
"""
        mock_dependencies = ProjectDependencies(
            runtime=["pkg4==3.1.4"], dev=list(), doc=list(), test=list()
        )

        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )

        with pytest.raises(
            DependencyCheckError,
            match=r"^Project dependencies not installed",
        ):
            _check_dependencies(MOCK_VENV_BIN_PATH, mock_dependencies, "all")

    def test_empty_dependencies(self, mocker):
        """No declared dependencies passes."""
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """
Package                       Version
----------------------------- ---------
"""
        mock_dependencies = ProjectDependencies(
            runtime=[], dev=list(), doc=list(), test=list()
        )

        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )

        _check_dependencies(MOCK_VENV_BIN_PATH, mock_dependencies, "all")

    def test_bad_venv_raises(self, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 1
        mock_dependencies = ProjectDependencies(
            runtime=["a==3.1.4"], dev=list(), doc=list(), test=list()
        )

        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )

        with pytest.raises(
            VenvPipError,
            match=r"^Failed to list installed virtual environment packages",
        ):
            _check_dependencies(MOCK_VENV_BIN_PATH, mock_dependencies, "all")


@pytest.fixture()
def mock_venv_create(mocker):
    def _apply(exists: bool) -> None:
        mocker.patch(
            "build_harness.commands.dependencies.pathlib.Path.exists",
            return_value=exists,
        )
        if not exists:
            # mock out the command that creates a venv
            mock_result = mocker.create_autospec(subprocess.CompletedProcess)
            mock_result.returncode = 0
            mock_result.stdout = """
some status
"""
            mock_result.stderr = ""
            mocker.patch(
                "build_harness.commands.dependencies.run_command",
                return_value=mock_result,
            )

    return _apply


class TestCheckVirtualEnvironment:
    def test_clean_create(self, mock_venv_create):
        mock_venv_create(False)

        result = _check_virtual_environment(MOCK_VENV_BIN_PATH)

        assert result == MOCK_VENV_BIN_PATH / ".venv" / "bin"

    def test_clean_exists(self, mocker, mock_venv_create):
        mock_venv_create(True)

        mocker.patch(
            "build_harness.commands.dependencies.pathlib.Path.is_file",
            return_value=True,
        )

        result = _check_virtual_environment(MOCK_VENV_BIN_PATH)

        assert result == MOCK_VENV_BIN_PATH / ".venv" / "bin"

    def test_command_fails(self, mocker, mock_venv_create):
        mock_venv_create(False)
        mocker.patch(
            "build_harness.commands.dependencies.pathlib.Path.exists",
            return_value=False,
        )
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 1
        mock_result.stdout = """
some status
"""
        mock_result.stderr = """
command failed
"""
        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )

        with pytest.raises(
            VenvError, match=r"^Failed creating virtual environment"
        ):
            _check_virtual_environment(MOCK_VENV_BIN_PATH)

    def test_bad_venv_bin_raises(self, mocker, mock_venv_create):
        mock_venv_create(True)

        mocker.patch(
            "build_harness.commands.dependencies.pathlib.Path.is_file",
            return_value=False,
        )

        with pytest.raises(VenvError, match=r"^Invalid virtual environment"):
            _check_virtual_environment(MOCK_VENV_BIN_PATH)


class TestInstallProjectDependencies:
    def test_default(self, mocker):
        mock_dependencies = [
            "toml == 3.1.4",
            "flit >=2.0,<4",
        ]
        mock_command = mocker.patch(
            "build_harness.commands.dependencies.run_command"
        )
        mock_command.return_value.returncode = 0

        _install_project_dependencies(mock_dependencies, MOCK_VENV_BIN_PATH)

        expected_stdin = "\n".join(mock_dependencies)
        mock_command.assert_called_once_with(
            [
                str(MOCK_VENV_BIN_PATH / "pip"),
                "install",
                "-r",
                "/dev/stdin",
            ],
            input=expected_stdin,
            text=True,
            capture_output=True,
            universal_newlines=True,
        )

    def test_install_raises(self, mocker):
        mock_dependencies = [
            "toml == 3.1.4",
            "flit >=2.0,<4",
        ]
        mock_command = mocker.patch(
            "build_harness.commands.dependencies.run_command"
        )
        mock_command.return_value.returncode = 1

        with pytest.raises(
            DependencyInstallError, match=r"^Dependency installation failed"
        ):
            _install_project_dependencies(mock_dependencies, MOCK_VENV_BIN_PATH)


class TestInstallAllProjectDependencies:
    def test_all(self, mocker):
        mock_project_dependencies = {
            "runtime": [
                "requests >=2.2, <3.0",
                "toml == 1.0.0",
            ],
            "dev": ["pre_commit == 2.7.1"],
            "doc": ["sphinx == 3.2.1"],
            "test": ["pytest == 6.1.1"],
        }
        mock_venv = pathlib.Path("/some/venv")
        mock_install = mocker.patch(
            "build_harness.commands.dependencies._install_project_dependencies"
        )

        _install_all_project_dependencies(mock_project_dependencies, mock_venv)

        mock_install.assert_called_once_with(
            [
                "requests >=2.2, <3.0",
                "toml == 1.0.0",
                "pre_commit == 2.7.1",
                "sphinx == 3.2.1",
                "pytest == 6.1.1",
            ],
            mock_venv,
        )


@pytest.fixture()
def mock_run(mock_sysargv, mocker):
    mock_pytest_result = mocker.create_autospec(subprocess.CompletedProcess)
    mock_pytest_result.returncode = 0
    mock_pytest_result.stdout = ""
    this_run = mocker.patch(
        "build_harness.commands.dependencies.run_command",
        return_value=mock_pytest_result,
    )

    return this_run


MOCK_DEPENDENCIES: ProjectDependencies = {
    "runtime": [
        "requests == 3.1.4",
    ],
    "dev": [
        "behave == 1.2.6",
    ],
    "doc": [
        "sphinx == 3.2.1",
    ],
    "test": [
        "pytest == 6.1.1",
    ],
}


@pytest.fixture()
def mock_dependencies(mocker):
    def _apply(venv_bin_path: pathlib.Path) -> typing.Any:
        mocker.patch(
            "build_harness.commands.dependencies.acquire_project_dependencies",
            return_value=copy.deepcopy(MOCK_DEPENDENCIES),
        )
        mock_check = mocker.patch(
            "build_harness.commands.dependencies._check_virtual_environment",
            return_value=venv_bin_path,
        )

        return mock_check

    return _apply


class TestInstall:
    def test_default(self, click_runner, mocker, mock_dependencies, mock_run):
        mock_check = mock_dependencies(MOCK_VENV_BIN_PATH)

        result = click_runner.invoke(
            main,
            [
                "install",
            ],
        )

        assert result.exit_code == 0
        mock_check.assert_called_once()
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        str(MOCK_VENV_BIN_PATH / "pip"),
                        "install",
                        "-r",
                        "/dev/stdin",
                    ],
                    capture_output=True,
                    input="requests == 3.1.4\nbehave == 1.2.6\nsphinx == "
                    "3.2.1\npytest == 6.1.1",
                    text=True,
                    universal_newlines=True,
                ),
            ]
        )

    def test_all(self, click_runner, mocker, mock_dependencies, mock_run):
        mock_check = mock_dependencies(MOCK_VENV_BIN_PATH)

        result = click_runner.invoke(
            main,
            [
                "install",
                "--dependencies",
                "all",
            ],
        )

        assert result.exit_code == 0
        mock_check.assert_called_once()
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        str(MOCK_VENV_BIN_PATH / "pip"),
                        "install",
                        "-r",
                        "/dev/stdin",
                    ],
                    capture_output=True,
                    input="requests == 3.1.4\nbehave == 1.2.6\nsphinx == 3.2.1\npytest == 6.1.1",
                    text=True,
                    universal_newlines=True,
                ),
            ]
        )

    def test_runtime(self, click_runner, mocker, mock_dependencies, mock_run):
        mock_check = mock_dependencies(MOCK_VENV_BIN_PATH)

        result = click_runner.invoke(
            main,
            [
                "install",
                "--dependencies",
                "runtime",
            ],
        )

        assert result.exit_code == 0
        mock_check.assert_called_once()
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        str(MOCK_VENV_BIN_PATH / "pip"),
                        "install",
                        "-r",
                        "/dev/stdin",
                    ],
                    capture_output=True,
                    input="requests == 3.1.4",
                    text=True,
                    universal_newlines=True,
                ),
            ]
        )

    def test_dev(self, click_runner, mocker, mock_dependencies, mock_run):
        mock_check = mock_dependencies(MOCK_VENV_BIN_PATH)

        result = click_runner.invoke(
            main,
            [
                "install",
                "--dependencies",
                "dev",
            ],
        )

        assert result.exit_code == 0
        mock_check.assert_called_once()
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        str(MOCK_VENV_BIN_PATH / "pip"),
                        "install",
                        "-r",
                        "/dev/stdin",
                    ],
                    capture_output=True,
                    input="behave == 1.2.6",
                    text=True,
                    universal_newlines=True,
                ),
            ]
        )

    def test_doc(self, click_runner, mocker, mock_dependencies, mock_run):
        mock_check = mock_dependencies(MOCK_VENV_BIN_PATH)

        result = click_runner.invoke(
            main,
            [
                "install",
                "--dependencies",
                "doc",
            ],
        )

        assert result.exit_code == 0
        mock_check.assert_called_once()
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        str(MOCK_VENV_BIN_PATH / "pip"),
                        "install",
                        "-r",
                        "/dev/stdin",
                    ],
                    capture_output=True,
                    input="sphinx == 3.2.1",
                    text=True,
                    universal_newlines=True,
                ),
            ]
        )

    def test_test(self, click_runner, mocker, mock_dependencies, mock_run):
        mock_check = mock_dependencies(MOCK_VENV_BIN_PATH)

        result = click_runner.invoke(
            main,
            [
                "install",
                "--dependencies",
                "test",
            ],
        )

        assert result.exit_code == 0
        mock_check.assert_called_once()
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        str(MOCK_VENV_BIN_PATH / "pip"),
                        "install",
                        "-r",
                        "/dev/stdin",
                    ],
                    capture_output=True,
                    input="pytest == 6.1.1",
                    text=True,
                    universal_newlines=True,
                ),
            ]
        )

    def test_bad_pyprojecttoml(self, click_runner, mocker, mock_dependencies):
        mock_dependencies(MOCK_VENV_BIN_PATH)

        mocker.patch(
            "build_harness.commands.dependencies.acquire_project_dependencies",
            side_effect=PyprojecttomlError("Missing pyproject.toml file"),
        )
        result = click_runner.invoke(main, ["install"])

        assert result.exit_code == ExitState.BAD_PYPROJECTTOML.value
        assert "Missing pyproject.toml file" in result.output

    def test_fails(self, click_runner, mocker, mock_dependencies):
        mock_dependencies(MOCK_VENV_BIN_PATH)

        mocker.patch(
            "build_harness.commands.dependencies._install_project_dependencies",
            side_effect=DependencyInstallError(
                "Dependency installation failed"
            ),
        )
        result = click_runner.invoke(main, ["install"])

        assert result.exit_code == ExitState.DEPENDENCY_INSTALL_FAILED.value
        assert "Dependency installation failed" in result.output


class TestCheckArgument:
    def test_clean(self, click_runner, mocker, mock_dependencies):
        mock_dependencies(MOCK_VENV_BIN_PATH)

        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """
Package                       Version
----------------------------- ---------
pkg1                     0.7.12
pkg2                         20.8b1
requests   3.1.4
behave   1.2.6
sphinx   3.2.1
pytest   6.1.1
"""
        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )
        mocker.patch(
            "build_harness.commands.dependencies.acquire_project_dependencies",
            return_value=MOCK_DEPENDENCIES,
        )
        result = click_runner.invoke(main, ["install", "--check"])

        assert result.exit_code == 0

    def test_check_fails(self, click_runner, mocker, mock_dependencies):
        mock_dependencies(MOCK_VENV_BIN_PATH)

        mocker.patch(
            "build_harness.commands.dependencies._check_dependencies",
            side_effect=DependencyCheckError("Dependency check failed"),
        )
        result = click_runner.invoke(main, ["install", "--check"])

        assert result.exit_code == ExitState.DEPENDENCY_CHECK_FAILED.value
        assert "Dependency check failed" in result.output

    def test_pip_fails(self, click_runner, mocker, mock_dependencies):
        mock_dependencies(MOCK_VENV_BIN_PATH)

        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 1
        mocker.patch(
            "build_harness.commands.dependencies.run_command",
            return_value=mock_result,
        )
        result = click_runner.invoke(main, ["install", "--check"])

        assert result.exit_code == ExitState.DEPENDENCY_CHECK_FAILED.value
        assert (
            "Failed to list installed virtual environment packages"
            in result.output
        )
