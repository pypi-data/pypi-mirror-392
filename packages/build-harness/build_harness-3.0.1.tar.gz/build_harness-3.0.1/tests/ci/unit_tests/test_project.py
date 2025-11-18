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

import pytest

from build_harness.project import (
    DependencyValidationError,
    ProjectDependencyAnalysis,
    PyprojecttomlError,
    _acquire_pyprojecttoml_data,
    acquire_project_dependencies,
    acquire_source_dir,
)

MOCK_PROJECT_DIR = pathlib.Path("some/test_project/path")


class TestAcquirePyprojecttomlData:
    def test_flit(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=True
        )
        mock_open = mocker.mock_open(
            read_data="""
[tool.flit.metadata]
module = "some_source_dir"
"""
        )
        mocker.patch("build_harness.project.pathlib.Path.open", mock_open)

        result = _acquire_pyprojecttoml_data(MOCK_PROJECT_DIR)

        assert result == {
            "tool": {"flit": {"metadata": {"module": "some_source_dir"}}}
        }

    def test_no_pyprojecttoml(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=False
        )

        with pytest.raises(
            PyprojecttomlError, match="^Missing pyproject.toml file"
        ):
            _acquire_pyprojecttoml_data(MOCK_PROJECT_DIR)


class TestFlitProject:
    def test_flit(self, mocker):
        this_mock_data = {
            "build-system": {
                "requires": [
                    "flit >=2, <4",
                ],
            },
            "tool": {
                "flit": {
                    "metadata": {"module": "sample_project"},
                },
            },
        }
        mocker.patch(
            "build_harness.project._acquire_pyprojecttoml_data",
            return_value=this_mock_data,
        )

        result = acquire_source_dir(MOCK_PROJECT_DIR)

        assert result == "sample_project"

    def test_flit_core_old_style(self, mocker):
        this_mock_data = {
            "build-system": {
                "requires": [
                    "flit_core >=3, <4",
                ],
            },
            "tool": {
                "flit": {
                    "metadata": {"module": "sample_project"},
                },
            },
        }
        mocker.patch(
            "build_harness.project._acquire_pyprojecttoml_data",
            return_value=this_mock_data,
        )

        result = acquire_source_dir(MOCK_PROJECT_DIR)

        assert result == "sample_project"

    def test_flit_core_new_style(self, mocker):
        this_mock_data = {
            "build-system": {
                "requires": [
                    "flit_core >=3, <4",
                ],
            },
            "project": {"name": "sample_project"},
        }
        mocker.patch(
            "build_harness.project._acquire_pyprojecttoml_data",
            return_value=this_mock_data,
        )

        result = acquire_source_dir(MOCK_PROJECT_DIR)

        assert result == "sample_project"

    def test_missing_flit_project_name(self, mocker):
        this_mock_data = {
            "build-system": {
                "requires": [
                    "flit_core >=3, <4",
                ],
            },
        }
        mocker.patch(
            "build_harness.project._acquire_pyprojecttoml_data",
            return_value=this_mock_data,
        )
        with pytest.raises(
            PyprojecttomlError,
            match=r"^Malformed flit pyproject\.toml missing project name",
        ):
            acquire_source_dir(MOCK_PROJECT_DIR)

    def test_bad_build_system_raises(self, mocker):
        this_mock_data = {
            "build-system": {
                "requires": [
                    "invalid-system",
                ],
            },
        }
        mocker.patch(
            "build_harness.project._acquire_pyprojecttoml_data",
            return_value=this_mock_data,
        )

        with pytest.raises(
            PyprojecttomlError, match="^Invalid build system specified"
        ):
            acquire_source_dir(MOCK_PROJECT_DIR)

    def test_missing_build_system_raises(self, mocker):
        this_mock_data = {
            "build-system": {},
        }
        mocker.patch(
            "build_harness.project._acquire_pyprojecttoml_data",
            return_value=this_mock_data,
        )

        with pytest.raises(
            PyprojecttomlError,
            match="^Invalid pyproject.toml, missing build system specification",
        ):
            acquire_source_dir(MOCK_PROJECT_DIR)


class TestAcquireProjectDependencies:
    def test_flit_old_style_dependencies(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=True
        )
        mock_open = mocker.mock_open(
            read_data="""
[tool.flit.metadata]
requires = [
    "requests >=2.2, <3.0",
    "toml == 1.0.0",
]

[tool.flit.metadata.requires-extra]
dev = [
    "pre_commit == 2.7.1",
]
doc = [
    "sphinx == 3.2.1",
]
test = [
    "pytest == 6.1.1",
]
"""
        )
        mocker.patch("build_harness.project.pathlib.Path.open", mock_open)

        result = acquire_project_dependencies(MOCK_PROJECT_DIR)

        expected_data = {
            "runtime": [
                "requests >=2.2, <3.0",
                "toml == 1.0.0",
            ],
            "dev": ["pre_commit == 2.7.1"],
            "doc": ["sphinx == 3.2.1"],
            "test": ["pytest == 6.1.1"],
        }
        assert result == expected_data

    def test_flit_new_style_dependencies(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=True
        )
        mock_open = mocker.mock_open(
            read_data="""
[project]
requires = [
    "requests >=2.2, <3.0",
    "toml == 1.0.0",
]

[project.optional-dependencies]
dev = [
    "pre_commit == 2.7.1",
]
doc = [
    "sphinx == 3.2.1",
]
test = [
    "pytest == 6.1.1",
]
"""
        )
        mocker.patch("build_harness.project.pathlib.Path.open", mock_open)

        result = acquire_project_dependencies(MOCK_PROJECT_DIR)

        expected_data = {
            "runtime": [
                "requests >=2.2, <3.0",
                "toml == 1.0.0",
            ],
            "dev": ["pre_commit == 2.7.1"],
            "doc": ["sphinx == 3.2.1"],
            "test": ["pytest == 6.1.1"],
        }
        assert result == expected_data

    def test_missing_requires(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=True
        )
        mock_open = mocker.mock_open(
            read_data="""
[tool.flit.metadata]

[tool.flit.metadata.requires-extra]
dev = [
    "pre_commit == 2.7.1",
]
doc = [
    "sphinx == 3.2.1",
]
test = [
    "pytest == 6.1.1",
]
"""
        )
        mocker.patch("build_harness.project.pathlib.Path.open", mock_open)

        result = acquire_project_dependencies(MOCK_PROJECT_DIR)

        expected_data = {
            "runtime": [],
            "dev": ["pre_commit == 2.7.1"],
            "doc": ["sphinx == 3.2.1"],
            "test": ["pytest == 6.1.1"],
        }
        assert result == expected_data

    def test_missing_dev(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=True
        )
        mock_open = mocker.mock_open(
            read_data="""
[tool.flit.metadata]
requires = [
    "requests >=2.2, <3.0",
    "toml == 1.0.0",
]

[tool.flit.metadata.requires-extra]
doc = [
    "sphinx == 3.2.1",
]
test = [
    "pytest == 6.1.1",
]
"""
        )
        mocker.patch("build_harness.project.pathlib.Path.open", mock_open)

        result = acquire_project_dependencies(MOCK_PROJECT_DIR)

        expected_data = {
            "runtime": [
                "requests >=2.2, <3.0",
                "toml == 1.0.0",
            ],
            "dev": [],
            "doc": ["sphinx == 3.2.1"],
            "test": ["pytest == 6.1.1"],
        }
        assert result == expected_data

    def test_missing_doc(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=True
        )
        mock_open = mocker.mock_open(
            read_data="""
[tool.flit.metadata]
requires = [
    "requests >=2.2, <3.0",
    "toml == 1.0.0",
]

[tool.flit.metadata.requires-extra]
dev = [
    "pre_commit == 2.7.1",
]
test = [
    "pytest == 6.1.1",
]
"""
        )
        mocker.patch("build_harness.project.pathlib.Path.open", mock_open)

        result = acquire_project_dependencies(MOCK_PROJECT_DIR)

        expected_data = {
            "runtime": [
                "requests >=2.2, <3.0",
                "toml == 1.0.0",
            ],
            "dev": ["pre_commit == 2.7.1"],
            "doc": [],
            "test": ["pytest == 6.1.1"],
        }
        assert result == expected_data

    def test_missing_test(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=True
        )
        mock_open = mocker.mock_open(
            read_data="""
[tool.flit.metadata]
requires = [
    "requests >=2.2, <3.0",
    "toml == 1.0.0",
]

[tool.flit.metadata.requires-extra]
dev = [
    "pre_commit == 2.7.1",
]
doc = [
    "sphinx == 3.2.1",
]
"""
        )
        mocker.patch("build_harness.project.pathlib.Path.open", mock_open)

        result = acquire_project_dependencies(MOCK_PROJECT_DIR)

        expected_data = {
            "runtime": [
                "requests >=2.2, <3.0",
                "toml == 1.0.0",
            ],
            "dev": ["pre_commit == 2.7.1"],
            "doc": ["sphinx == 3.2.1"],
            "test": [],
        }
        assert result == expected_data

    def test_invalid_project(self, mocker):
        mocker.patch(
            "build_harness.project.pathlib.Path.is_file", return_value=True
        )
        mock_open = mocker.mock_open(
            read_data="""
[not.a.project]
"""
        )
        mocker.patch("build_harness.project.pathlib.Path.open", mock_open)
        with pytest.raises(
            PyprojecttomlError,
            match=r"^Invalid pyproject\.toml project specification",
        ):
            acquire_project_dependencies(MOCK_PROJECT_DIR)


class TestProjectDependencyAnalysis:
    # https://www.python.org/dev/peps/pep-0440/#version-specifiers
    MOCK_DEPENDENCIES = {
        "runtime": [
            "compatible1 ~= 3.1.4",
            "compatible2 ~= 3.1",
            "version_matching == 3.1.4",
            "version_exclusion != 3.1.4",
            "inclusive_ordered1 <=3.1.4",
            "inclusive_ordered2 >=3.1.4",
            "exclusive_ordered1 <3.1.4",
            "exclusive_ordered2 >3.1.4",
            "arbitrary_equality === custom4rel",
            "runtime_exclusive == 3.1.4",
            "multiple_specifiers >=2.2, <3.0",
            "empty_specifier",
        ],
        "dev": ["dev_exclusive == 3.1.4"],
        "doc": ["doc_exclusive == 3.1.4"],
        "test": ["test_exclusive == 3.1.4"],
    }

    def test_all(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert under_test.packages == [
            "compatible1",
            "compatible2",
            "version_matching",
            "version_exclusion",
            "inclusive_ordered1",
            "inclusive_ordered2",
            "exclusive_ordered1",
            "exclusive_ordered2",
            "arbitrary_equality",
            "runtime_exclusive",
            "multiple_specifiers",
            "empty_specifier",
            "dev_exclusive",
            "doc_exclusive",
            "test_exclusive",
        ]

        assert under_test.valid_release("runtime_exclusive", "3.1.4")
        assert under_test.valid_release("dev_exclusive", "3.1.4")
        assert under_test.valid_release("doc_exclusive", "3.1.4")
        assert under_test.valid_release("test_exclusive", "3.1.4")

    def test_runtime(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "runtime"
        )

        assert under_test.packages == [
            "compatible1",
            "compatible2",
            "version_matching",
            "version_exclusion",
            "inclusive_ordered1",
            "inclusive_ordered2",
            "exclusive_ordered1",
            "exclusive_ordered2",
            "arbitrary_equality",
            "runtime_exclusive",
            "multiple_specifiers",
            "empty_specifier",
        ]

    def test_dev(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "dev"
        )

        assert under_test.packages == [
            "dev_exclusive",
        ]

    def test_doc(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "doc"
        )

        assert under_test.packages == [
            "doc_exclusive",
        ]

    def test_test(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "test"
        )

        assert under_test.packages == [
            "test_exclusive",
        ]

    def test_compatible1(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert not under_test.valid_release("compatible1", "4.0")
        assert not under_test.valid_release("compatible1", "3.1.3")
        assert not under_test.valid_release("compatible1", "3.2")
        assert under_test.valid_release("compatible1", "3.1.4")
        assert under_test.valid_release("compatible1", "3.1.5")

    def test_compatible2(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert not under_test.valid_release("compatible2", "4.0")
        assert not under_test.valid_release("compatible2", "3.0")
        assert under_test.valid_release("compatible2", "3.1.3")
        assert under_test.valid_release("compatible2", "3.2")

    def test_version_matching(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert under_test.valid_release("version_matching", "3.1.4")
        assert not under_test.valid_release("version_matching", "3.1.3")
        assert not under_test.valid_release("version_matching", "3.1.5")

    def test_version_exclusion(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert not under_test.valid_release("version_exclusion", "3.1.4")
        assert under_test.valid_release("version_exclusion", "3.1.3")
        assert under_test.valid_release("version_exclusion", "3.1.5")

    def test_inclusive_ordered1(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert under_test.valid_release("inclusive_ordered1", "3.1.4")
        assert under_test.valid_release("inclusive_ordered1", "3.1.3")
        assert not under_test.valid_release("inclusive_ordered1", "3.1.5")

    def test_inclusive_ordered2(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert under_test.valid_release("inclusive_ordered2", "3.1.4")
        assert not under_test.valid_release("inclusive_ordered2", "3.1.3")
        assert under_test.valid_release("inclusive_ordered2", "3.1.5")

    def test_exclusive_ordered1(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert not under_test.valid_release("exclusive_ordered1", "3.1.4")
        assert under_test.valid_release("exclusive_ordered1", "3.1.3")
        assert not under_test.valid_release("exclusive_ordered1", "3.1.5")

    def test_exclusive_ordered2(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert not under_test.valid_release("exclusive_ordered2", "3.1.4")
        assert not under_test.valid_release("exclusive_ordered2", "3.1.3")
        assert under_test.valid_release("exclusive_ordered2", "3.1.5")

    @pytest.mark.skip("arbitrary equality not supported")
    def test_arbitrary_equality(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert under_test.valid_release("arbitrary_equality", "custom4rel")
        assert not under_test.valid_release("arbitrary_equality", "3.1.3")

    def test_multiple_specifiers(self):
        mock_dependencies = {
            "runtime": [
                "multiple_specifiers >=2.2, <3.0",
            ],
            "dev": list(),
            "doc": list(),
            "test": list(),
        }
        under_test = ProjectDependencyAnalysis(mock_dependencies, "all")

        assert under_test.valid_release("multiple_specifiers", "2.2")
        assert not under_test.valid_release("multiple_specifiers", "2.1")
        assert not under_test.valid_release("multiple_specifiers", "3.0")

    def test_empty_specifier(self):
        """any release id is valid for an empty specifier"""
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )

        assert under_test.valid_release("empty_specifier", "3.1.4")
        assert under_test.valid_release("empty_specifier", "1")
        assert under_test.valid_release("empty_specifier", "22")

    def test_missing_package_raises(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "all"
        )
        with pytest.raises(
            DependencyValidationError,
            match=r"^Package not found in dependencies",
        ):
            under_test.valid_release("bad_package", "3.1.4")

    def test_runtime_exclusive(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "runtime"
        )
        assert under_test.valid_release("runtime_exclusive", "3.1.4")
        assert not under_test.valid_release("runtime_exclusive", "4")
        with pytest.raises(
            DependencyValidationError,
            match=r"^Package not found in dependencies",
        ):
            under_test.valid_release("dev_exclusive", "3.1.4")

    def test_dev_exclusive(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "dev"
        )
        assert under_test.valid_release("dev_exclusive", "3.1.4")
        with pytest.raises(
            DependencyValidationError,
            match=r"^Package not found in dependencies",
        ):
            under_test.valid_release("runtime_exclusive", "3.1.4")

    def test_doc_exclusive(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "doc"
        )
        assert under_test.valid_release("doc_exclusive", "3.1.4")
        with pytest.raises(
            DependencyValidationError,
            match=r"^Package not found in dependencies",
        ):
            under_test.valid_release("dev_exclusive", "3.1.4")

    def test_test_exclusive(self):
        under_test = ProjectDependencyAnalysis(
            copy.deepcopy(self.MOCK_DEPENDENCIES), "test"
        )
        assert under_test.valid_release("test_exclusive", "3.1.4")
        with pytest.raises(
            DependencyValidationError,
            match=r"^Package not found in dependencies",
        ):
            under_test.valid_release("dev_exclusive", "3.1.4")
