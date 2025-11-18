#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Dependency installation subcommand implementation."""

import io
import logging
import pathlib
import re
import sys
import typing

import click

from build_harness._utility import report_console_error, run_command
from build_harness.project import (
    DEPENDENCY_TYPES,
    DependencyValidationError,
    ProjectDependencies,
    ProjectDependencyAnalysis,
    PyprojecttomlError,
    acquire_project_dependencies,
)
from build_harness.tools import Pep426Patterns, Pep440Patterns, pep503_normalize

from .state import CommandState, ExitState

log = logging.getLogger(__name__)

VALID_DEPENDENCY_CHOICES = [
    "all",
    "dev",
    "runtime",
    "doc",
    "test",
]


class BootstrapError(Exception):
    """Problem occurred during dependency installation."""


class DependencyCheckError(BootstrapError):
    """Installed project dependencies failed to align with declarations."""


class DependencyInstallError(BootstrapError):
    """Problem occurred during pip installation of project dependencies."""


class VenvError(BootstrapError):
    """Problem occurred creating or validating the virtual environment."""


class VenvPipError(BootstrapError):
    """Problem occurred using virtual environment pip."""


PIP_LIST_PATTERN = re.compile(
    r"^\s*{0}\s+(?P<release_id>{1})".format(
        Pep426Patterns.UNNORMALIZED_PACKAGE_NAME,
        Pep440Patterns.VALID_VERSION_CHARACTERS,
    )
)

PipList = typing.List[typing.Tuple[str, str]]


def _extract_pip_list_packages(pip_output: str) -> PipList:
    with io.StringIO(initial_value=pip_output) as f:
        lines = f.readlines()

    pip_list: PipList = []
    for this_line in lines:
        result = PIP_LIST_PATTERN.search(this_line)
        if (
            (result is not None)
            and (result.group("package_name") != "Package")
            and (not result.group("package_name").startswith("--"))
        ):
            pip_list.append(
                (
                    pep503_normalize(result.group("package_name")),
                    result.group("release_id"),
                )
            )

    return pip_list


def _check_pip_versions(
    pip_list: typing.List[typing.Tuple[str, str],],
    analysis: ProjectDependencyAnalysis,
) -> None:
    """
    Check that pip installed versions align with project declared dependencies.

    Args:
        pip_list:
        analysis:

    Raises:
        DependencyCheckError: If there is a version mismatch.
    """
    validated_releases = []
    failed_packages = []
    for package_name, package_release in pip_list:
        try:
            validated = analysis.valid_release(package_name, package_release)

            validated_releases.append(validated)
            if not validated:
                failed_packages.append((package_name, package_release))
        except DependencyValidationError:
            # ignore packages that are installed in pip venv, but not declared
            # in project dependencies.
            pass

    if not all(validated_releases):
        raise DependencyCheckError(
            "Installed packages do not comply with declared project "
            "dependencies, {0}".format(failed_packages)
        )


def _check_dependency_names(
    pip_list: typing.List[typing.Tuple[str, str],],
    analysis: ProjectDependencyAnalysis,
) -> None:
    """
    Check that project dependencies are installed in the virtual environment.

    Args:
        pip_list: List of packages installed in virtual environment.
        analysis: Project dependencies analysis object.

    Raises:
        DependencyCheckError: If there is a version mismatch.
    """
    project_packages = analysis.packages
    pip_package_names = [pep503_normalize(x) for x, y in pip_list]

    missing_packages = [
        x
        for x in project_packages
        if pep503_normalize(x) not in pip_package_names
    ]
    if len(missing_packages) != 0:
        raise DependencyCheckError(
            "Project dependencies not installed, {0}".format(missing_packages)
        )


def _check_dependencies(
    venv_path: pathlib.Path,
    project_dependencies: ProjectDependencies,
    dependency_type: DEPENDENCY_TYPES,
) -> None:
    """
    Check project dependencies.

    Checks that virtual environment dependencies are aligned with project
    dependencies declarations.

    Args:
        venv_path:
        project_dependencies:
        dependency_type:

    Raises:
        DependencyCheckError: If dependency check fails.
    """
    analysis = ProjectDependencyAnalysis(project_dependencies, dependency_type)

    venv_pip = venv_path / "pip"
    result = run_command(
        [str(venv_pip), "list"],
        capture_output=True,
        text=True,
        universal_newlines=True,
    )
    if result.returncode != 0:
        raise VenvPipError(
            "Failed to list installed virtual environment packages, "
            "{0}".format(venv_path)
        )
    else:
        pip_list = _extract_pip_list_packages(result.stdout)
        _check_pip_versions(pip_list, analysis)
        _check_dependency_names(pip_list, analysis)


def _check_virtual_environment(project_path: pathlib.Path) -> pathlib.Path:
    """
    Check if the necessary virtual environment exists, creating it if needed.

    Args:
        project_path: Project repo root directory.

    Returns:
        Path to virtual environment bin directory.
    """
    expected_venv_path = project_path / ".venv" / "bin"

    if not expected_venv_path.exists():
        result = run_command(
            ["python3", "-m", "venv", str(expected_venv_path.parent)],
            capture_output=True,
            universal_newlines=True,
        )

        if result.returncode != 0:
            message = "Failed creating virtual environment, {0}".format(
                expected_venv_path.parent
            )
            log.error(message)
            if result.stdout:
                log.error("Venv stdout, {0}".format(result.stdout))
            if result.stderr:
                log.error("Venv stderr, {0}".format(result.stderr))
            raise VenvError(message)
    elif not (expected_venv_path / "pip").is_file():
        # Assume it's an invalid virtual environment
        message = "Invalid virtual environment, {0}".format(expected_venv_path)
        raise VenvError(message)

    return expected_venv_path


def _install_project_dependencies(
    dependencies: typing.List[str], venv_path: pathlib.Path
) -> None:
    """
    Install the specified project dependencies to the virtual environment.

    Args:
        dependencies: List of project dependencies to be installed.
        venv_path: Path to virtual environment bin directory.

    Raises:
        DependencyInstallError: If installation does not exit cleanly.
    """
    dependency_input = "\n".join(dependencies)
    result = run_command(
        [str(venv_path / "pip"), "install", "-r", "/dev/stdin"],
        capture_output=True,
        input=dependency_input,
        text=True,
        universal_newlines=True,
    )

    if result.returncode != 0:
        message = "Dependency installation failed"
        log.error(message)
        log.error("Pip install stdout, {0}".format(result.stdout))
        log.error("Pip install stderr, {0}".format(result.stderr))
        raise DependencyInstallError(message)


def _install_all_project_dependencies(
    project_dependencies: ProjectDependencies, venv_path: pathlib.Path
) -> None:
    """
    Install *all* the project dependencies to the virtual environment.

    Args:
        project_dependencies: Dictionary of project dependencies.
        venv_path: Path to virtual environment bin directory.

    Raises:
        DependencyInstallError: If installation does not exit cleanly.
    """
    aggregate: typing.List[str] = []
    for this_values in project_dependencies.values():
        aggregate += this_values  # type: ignore

    _install_project_dependencies(aggregate, venv_path)


@click.command()
@click.pass_context
@click.option(
    "--check",
    "check_dependencies",
    default=False,
    help="Don't install dependencies, just check if dependencies installed are "
    "consistent with the project requirements (pyproject.toml or "
    "requirements.txt).",
    is_flag=True,
)
@click.option(
    "--dependencies",
    "dependency_type",
    default="all",
    help="Install project package dependencies into virtual environment, "
    "creating the virtual environment if necessary.",
    show_default=True,
    type=click.Choice(VALID_DEPENDENCY_CHOICES, case_sensitive=True),
)
def install(
    ctx: click.Context,
    check_dependencies: bool,
    dependency_type: DEPENDENCY_TYPES,
) -> None:
    """
    Install project dependencies.

    If  virtual environment does not presently exist, one will be created.
    """
    try:
        ctx.ensure_object(dict)
        command_state: CommandState = ctx.obj["command_state"]

        project_dependencies = acquire_project_dependencies(
            command_state.project_path
        )

        # Cannot assume venv_path of this build_harness call is in or related
        # to the target project; user might be bootstrapping using build_
        # harness from another virtual environment.
        venv_path = _check_virtual_environment(command_state.project_path)

        if not check_dependencies:
            if dependency_type == "all":
                _install_all_project_dependencies(
                    project_dependencies, venv_path
                )
            else:
                _install_project_dependencies(
                    # mypy and dynamic data on TypedDict hints again
                    project_dependencies[dependency_type],  # type: ignore
                    venv_path,
                )
        else:
            _check_dependencies(
                venv_path, project_dependencies, dependency_type
            )
    except PyprojecttomlError as e:
        message = str(e)
        report_console_error(message)
        sys.exit(ExitState.BAD_PYPROJECTTOML.value)
    except (DependencyInstallError, VenvError) as e:
        message = str(e)
        report_console_error(message)
        sys.exit(ExitState.DEPENDENCY_INSTALL_FAILED.value)
    except (DependencyCheckError, VenvPipError) as e:
        message = str(e)
        report_console_error(message)
        sys.exit(ExitState.DEPENDENCY_CHECK_FAILED.value)
    except Exception:
        message = "Unexpected error. Check log for details."
        log.exception(message)
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
