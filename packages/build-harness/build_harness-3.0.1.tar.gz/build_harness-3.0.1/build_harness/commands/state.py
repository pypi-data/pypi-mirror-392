#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Define exit state numbers for build harness CLI."""

import dataclasses
import enum
import pathlib


@dataclasses.dataclass
class CommandState:
    """Global click command state context."""

    project_path: pathlib.Path
    venv_path: pathlib.Path


@enum.unique
class ExitState(enum.Enum):
    """Exit state enumeration."""

    UNKNOWN_ERROR = 100

    FORMATTING_FAILED = 110
    ISORT_CHECK_FAILED = 111
    BLACK_CHECK_FAILED = 112

    STATIC_ANALYSIS_FAILED = 120
    FLAKE8_FAILED = 121
    MYPY_FAILED = 122

    TESTS_FAILED = 130
    TEST_COVERAGE_FAILED = 131

    ACCEPTANCE_RUN_FAILED = 140
    ACCEPTANCE_TESTS_FAILED = 141

    DEPENDENCY_INSTALL_FAILED = 150
    DEPENDENCY_CHECK_FAILED = 151

    PACKAGING_FAILED = 160

    PUBLISHING_FAILED = 170

    BAD_VERSION = 180
    BAD_REPO = 190
    BAD_GIT_EXE = 200
    BAD_PYPROJECTTOML = 210

    BOOTSTRAP_FAILED = 220
