#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#


"""Acceptance tests subcommand implementation."""

import logging
import pathlib
import typing

from build_harness._base_exception import BuildHarnessError
from build_harness._utility import command_path, run_command

log = logging.getLogger(__name__)


class AcceptanceTestsError(BuildHarnessError):
    """Problem occurred during acceptance tests run."""


def _check_junit_dir(
    junit_xml_enabled: bool, junitxml_dir: pathlib.Path
) -> None:
    if junit_xml_enabled and (not junitxml_dir.exists()):
        junitxml_dir.mkdir(parents=True)
    elif junit_xml_enabled and (not junitxml_dir.is_dir()):
        raise AcceptanceTestsError(
            "JUnit XML location must be a directory, {0}".format(junitxml_dir)
        )


def _run_bdd(
    venv_path: pathlib.Path,
    junit_xml_enabled: bool,
    junitxml_dir: pathlib.Path,
    tags: typing.Tuple[typing.Optional[str]],
) -> None:
    _check_junit_dir(junit_xml_enabled, junitxml_dir)

    behave_command = [
        "behave",
        "--format",
        "pretty",
    ]

    if junit_xml_enabled:
        behave_command += [
            "--junit",
            "--junit-directory",
            str(junitxml_dir),
        ]

    behave_command += [
        "--tags",
        "~@notimplemented",
        "--tags",
        "~@nottestable",
    ]

    for this_tags in tags:
        if this_tags:
            behave_command += [
                "--tags",
                this_tags,
            ]

    behave_command += [
        "features",
    ]
    behave_command[0] = command_path(venv_path, behave_command)
    behave_result = run_command(behave_command)

    if behave_result.returncode != 0:
        raise AcceptanceTestsError("behave tests run failed")
