#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Manage acquisition of project metadata."""

import pathlib
import typing

import toml
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from build_harness.typing import Literal, TypedDict

from ._base_exception import BuildHarnessError
from .tools import Pep440Patterns, pep503_normalize


class DependencyValidationError(BuildHarnessError):
    """Problem has occurred validation a dependency package."""


class PyprojecttomlError(BuildHarnessError):
    """Problem has occurred loading ``pyproject.toml`` file."""


DEPENDENCY_TYPES = Literal["runtime", "dev", "doc", "test"]


class ProjectDependencies(TypedDict):
    """Project package dependencies dictionary type hint."""

    runtime: typing.List[str]
    dev: typing.List[str]
    doc: typing.List[str]
    test: typing.List[str]


def _acquire_pyprojecttoml_data(
    project_root: pathlib.Path,
) -> typing.MutableMapping[str, typing.Any]:
    """
    Load data from Python project ``pyproject.toml`` file.

    Args:
        project_root: Path to project root directory.

    Returns:
        Loaded TOML data
    Raises:
        PyprojecttomlError: if file cannot be loaded.
    """
    pyproject_toml_path = project_root / "pyproject.toml"
    if pyproject_toml_path.is_file():
        with pyproject_toml_path.open(mode="r") as f:
            content = f.read()
            toml_data = toml.loads(content)
    else:
        raise PyprojecttomlError(
            "Missing pyproject.toml file, {0}".format(pyproject_toml_path)
        )

    return toml_data


def acquire_source_dir(project_dir: pathlib.Path) -> str:
    """
    Acquire a project root source package from a project directory.

    Args:
        project_dir: Project root directory.

    Returns:
        Name of project root source package.
    Raises:
        PyprojecttomlError: If pyproject.toml does not specify the correct
                            build-system, or build-system specific configuration
                            is malformed.
    """
    toml_data = _acquire_pyprojecttoml_data(project_dir)

    try:
        build_system_requires = toml_data["build-system"]["requires"]

        if not any(x.startswith("flit") for x in build_system_requires):
            raise PyprojecttomlError("Invalid build system specified")
    except KeyError as e:
        raise PyprojecttomlError(
            "Invalid pyproject.toml, missing build system specification"
        ) from e

    try:
        root_module = toml_data["tool"]["flit"]["metadata"]["module"]
    except KeyError:
        try:
            root_module = toml_data["project"]["name"]
        except KeyError as e:
            raise PyprojecttomlError(
                "Malformed flit pyproject.toml missing project name"
            ) from e

    return root_module


def _acquire_runtime_dependencies(
    toml_data: typing.MutableMapping[str, typing.Any]
) -> typing.List[str]:
    try:
        if "requires" in toml_data["tool"]["flit"]["metadata"]:
            return toml_data["tool"]["flit"]["metadata"]["requires"]
    except KeyError:
        try:
            if "requires" in toml_data["project"]:
                return toml_data["project"]["requires"]
        except KeyError as e:
            raise PyprojecttomlError(
                "Invalid pyproject.toml project specification"
            ) from e

    # There's no "requires" field in either type of project specification.
    return []


def _acquire_nonruntime_dependencies(
    toml_data: typing.MutableMapping[str, typing.Any]
) -> typing.Dict[str, typing.Any]:
    result: typing.Dict[str, typing.Any] = {
        "dev": [],
        "doc": [],
        "test": [],
    }

    def _acquire_keys(_this_data: dict) -> None:
        for key in ["dev", "doc", "test"]:
            if key in _this_data:
                result[key] = _this_data[key]

    try:
        if "requires-extra" in toml_data["tool"]["flit"]["metadata"]:
            _acquire_keys(
                toml_data["tool"]["flit"]["metadata"]["requires-extra"]
            )
    except KeyError:
        try:
            if "optional-dependencies" in toml_data["project"]:
                _acquire_keys(toml_data["project"]["optional-dependencies"])
        except KeyError as e:
            raise PyprojecttomlError(
                "Invalid pyproject.toml optional dependency specification"
            ) from e

    return result


def acquire_project_dependencies(
    project_dir: pathlib.Path,
) -> ProjectDependencies:
    """
    Acquire Python project package dependencies from project definition.

    Args:
        project_dir: Root directory of project repo.

    Returns:
        Project package dependencies.
    """
    toml_data = _acquire_pyprojecttoml_data(project_dir)

    result: ProjectDependencies = {  # type: ignore
        "runtime": _acquire_runtime_dependencies(toml_data),
        **_acquire_nonruntime_dependencies(toml_data),  # type: ignore
    }

    return result


T = typing.TypeVar("T", bound="ProjectDependencyAnalysis")


class ProjectDependencyAnalysis:
    """
    Query project dependencies for valid releases.

    https://www.python.org/dev/peps/pep-0440/#version-specifiers
    """

    __dependency_list: typing.List[str]

    def __init__(
        self: T,
        dependencies: ProjectDependencies,
        dependency_type: DEPENDENCY_TYPES,
    ) -> None:
        """
        Project release queries.

        Args:
            dependencies: Dictionary of project dependencies.
            dependency_type: Type of dependency to validate.
        """
        self.dependency_type = dependency_type
        self.dependencies = dependencies

        if self.dependency_type == "all":
            self.__dependency_list = []
            for x in self.dependencies.values():
                self.__dependency_list += x
        else:
            self.__dependency_list = self.dependencies[self.dependency_type]

    @property
    def packages(self: T) -> typing.List[str]:
        """List of project packages for the specified dependency type."""
        value = []
        for this_package in self.__dependency_list:
            this_match = Pep440Patterns.SPECIFIER_PATTERN.search(this_package)
            if this_match is not None:
                value.append(this_match.group("package_name"))

        return value

    def valid_release(self: T, package_name: str, release_id: str) -> bool:
        """
        Indicate if the specified  release is valid for listed dependencies.

        Assumes the dependencies have been recovered from pyproject.toml or
        similar. Raises an exception if the package does not exist within the
        dependency type specified at construction.

        NOTE: arbitrary equality is not supported; appears to not be supported
        by the ``packaging`` library.

        https://www.python.org/dev/peps/pep-0440/#arbitrary-equality

        Args:
            package_name:
            release_id:

        Returns:
            True if the package release is valid. False otherwise.
        Raises:
            DependencyValidationError: If the package is not present in the
            dependency list.
        """
        version_spec = Version(release_id)
        normalized_package_name_spec = pep503_normalize(package_name)

        is_valid_release = False
        found_in_dependencies = False
        for this_package in self.__dependency_list:
            this_match = Pep440Patterns.SPECIFIER_PATTERN.search(this_package)
            if this_match is not None:
                dependency_name = pep503_normalize(
                    this_match.group("package_name")
                )

                if normalized_package_name_spec == dependency_name:
                    found_in_dependencies = True
                    # validate the release id
                    specifier_list_text = this_match.group("specifier_sets")

                    specifier_sets: typing.Optional[SpecifierSet]
                    if not specifier_list_text:
                        specifier_sets = SpecifierSet()
                    else:
                        specifiers = (
                            specifier_list_text.split(",")
                            if specifier_list_text
                            else []
                        )

                        specifier_sets = SpecifierSet(specifiers[0])
                        for this_text in specifiers[1::]:
                            specifier_sets &= SpecifierSet(this_text)

                    is_valid_release = version_spec in specifier_sets

        if not found_in_dependencies:
            raise DependencyValidationError(
                "Package not found in dependencies, {0}".format(package_name)
            )

        return is_valid_release
