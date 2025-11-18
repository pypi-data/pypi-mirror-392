#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Manage pytest command options."""

import logging
import pathlib
import typing

from build_harness._utility import command_path

log = logging.getLogger(__name__)

VALID_COVERAGE_REPORTS = ["html", "term-missing", "xml"]

ReportFlags = typing.TypedDict(
    "ReportFlags",
    {
        "junitxml": bool,
        "html": bool,
        "term-missing": bool,
        "xml": bool,
    },
)

ReportPaths = typing.TypedDict(
    "ReportPaths",
    {
        "junitxml": typing.Optional[pathlib.Path],
        # Coverage reports
        "html": typing.Optional[pathlib.Path],
        "term-missing": None,
        "xml": typing.Optional[pathlib.Path],
    },
)


class CommandOptionsTestTool(typing.TypedDict):
    """``pytest`` command options dictionary type hint."""

    output_path: pathlib.Path
    source_path: pathlib.Path
    test_path: pathlib.Path
    venv_path: pathlib.Path

    pass_zero_tests: bool

    report_enabled: ReportFlags
    report_dirs: ReportPaths


T = typing.TypeVar("T", bound="PytestCommand")


class PytestCommand:
    """Manage pytest command line options."""

    COVERAGE_REPORTS = [
        "html",
        "term-missing",
        "xml",
    ]

    def __init__(self: T, command_options: CommandOptionsTestTool) -> None:
        """Construct ``PytestCommand`` object."""
        self.options = command_options

    def command(self: T) -> typing.List[str]:
        """
        Construct pytest command list with argument options.

        Returns:
            Constructed list.
        """
        this_command = [
            "pytest",
        ]

        if any(
            self.options["report_enabled"][x]  # type:ignore
            for x in self.options["report_enabled"].keys()
        ):
            this_command.append(
                "--cov={0}".format(str(self.options["source_path"]))
            )

        for report, enabled in sorted(self.options["report_enabled"].items()):
            dirs_value = self.options["report_dirs"][report]  # type:ignore
            if enabled and (report in self.COVERAGE_REPORTS):
                this_command.append("--cov-report")
                argument = (
                    "{0}".format(report)
                    if not dirs_value
                    else "{0}:{1}".format(report, dirs_value)
                )
                this_command.append(argument)
            elif enabled and (report == "junitxml"):
                argument = (
                    "--junitxml"
                    if not dirs_value
                    else "--junitxml={0}".format(dirs_value)
                )
                this_command.append(argument)

        this_command.append(str(self.options["test_path"]))

        this_command[0] = command_path(self.options["venv_path"], this_command)
        return this_command
