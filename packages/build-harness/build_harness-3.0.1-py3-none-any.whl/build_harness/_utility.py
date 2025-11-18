#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""General support for build harness implementation."""

import logging
import pathlib
import re
import subprocess  # noqa: S404
import typing

import click

log = logging.getLogger(__name__)

CommandArgs = typing.List[str]


def command_path(venv_path: pathlib.Path, command_array: CommandArgs) -> str:
    """Construct command path, including virtual environment path."""
    this_path = str(venv_path / command_array[0])
    log.debug("command path, {0}".format(this_path))

    return this_path


def run_command(
    command: CommandArgs,
    suppress_command_logging: bool = False,
    suppress_argument_logging: bool = False,
    **kwargs: typing.Any,
) -> subprocess.CompletedProcess:
    """
    Run a system command using ``subprocess.run``.

    Args:
        command: List of command and arguments.
        suppress_command_logging: Suppress logging of command.
        suppress_argument_logging: Suppress logging of subprocess run command
                                   arguments.
        **kwargs: Optional arguments passed through to ``subprocess.run``.

    Returns:
        Subprocess results.
    """
    if not suppress_command_logging:
        log.debug("command to run, {0}".format(str(command)))
    if not suppress_argument_logging:
        log.debug("command arguments, {0}".format(str(kwargs)))
    final_args = {
        **kwargs,
        **{
            # always return text as string, not bytes
            "text": True,
        },
    }
    result = subprocess.run(command, **final_args)  # noqa: S603 S604

    log.debug("command return code, {0}".format(result.returncode))
    log.debug("command stdout, {0}".format(result.stdout))
    log.debug("command stderr, {0}".format(result.stderr))

    return result


def extract_coverage(report: str) -> int:
    """
    Extract total coverage result from a coverage report.

    Args:
        report: IO stream of captured coverage report output.

    Returns:
        Extracted total reported coverage.
    """
    current_coverage = 0
    lines = report.splitlines()
    for this_line in lines:
        match_result = re.search(
            r"^\s*((TOTAL)|((T|t)otal)).*\s+(?P<total>\d{1,3})%\s*$", this_line
        )  # type: ignore
        if match_result is not None:
            log.debug("coverage report line total, {0}".format(this_line))
            current_coverage = int(match_result.group("total"))  # type: ignore

    return current_coverage


def report_console_error(message: str) -> None:
    """
    Report an error to the click console.

    Args:
        message: Message to be reported.
    """
    click.echo(
        click.style("FAILED: {0}".format(message), bold=True, fg="red"),
        err=True,
    )
