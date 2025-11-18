#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Formatting subcommand implementation."""

import copy
import logging
import pathlib
import sys

import click

from build_harness._utility import (
    CommandArgs,
    command_path,
    report_console_error,
    run_command,
)

from .state import CommandState, ExitState

BLACK_FORMAT_CMD: CommandArgs = ["black", "."]
ISORT_FORMAT_CMD: CommandArgs = ["isort", "--profile", "black", "."]

BLACK_CHECK_CMD: CommandArgs = ["black", "--check", "."]
ISORT_CHECK_CMD: CommandArgs = ["isort", "--profile", "black", "--diff", "."]

log = logging.getLogger(__name__)


class FormattingError(Exception):
    """Problem occurred during code formatting."""


class IsortCheckError(Exception):
    """The isort formatting check failed."""


class BlackCheckError(Exception):
    """The black formatting check failed."""


def _apply_formatting(venv_path: pathlib.Path) -> None:
    """
    Apply formatting to source code.

    Args:
        venv_path: Path to Python virtual environment.

    Raises:
        FormattingError: If either isort or black exit non-zero.
    """
    click.echo("isort formatting...")
    isort_cmd = copy.deepcopy(ISORT_FORMAT_CMD)
    isort_cmd[0] = command_path(venv_path, isort_cmd)
    isort_result = run_command(isort_cmd)
    click.echo(click.style("isort completed", fg="green"))

    click.echo("black formatting...")
    black_cmd = copy.deepcopy(BLACK_FORMAT_CMD)
    black_cmd[0] = command_path(venv_path, black_cmd)
    black_result = run_command(black_cmd)
    click.echo(click.style("black completed", fg="green"))

    if any(x != 0 for x in [isort_result.returncode, black_result.returncode]):
        raise FormattingError("isort and/or black failed during formatting.")


def _check_formatting(venv_path: pathlib.Path) -> None:
    """
    Check if any formatting changes are needed on the code base.

    Args:
        venv_path: Path to Python virtual environment.

    Raises:
        BlackCheckError: If black formatting check fails.
        IsortCheckError: If isort formatting check fails.
    """
    click.echo("isort formatting check...")
    isort_cmd = copy.deepcopy(ISORT_CHECK_CMD)
    isort_cmd[0] = command_path(venv_path, isort_cmd)
    isort_result = run_command(isort_cmd)
    if isort_result.returncode != 0:
        raise IsortCheckError("isort check failed")
    click.echo(click.style("isort check completed", fg="green"))

    click.echo("black formatting check...")
    black_cmd = copy.deepcopy(BLACK_CHECK_CMD)
    black_cmd[0] = command_path(venv_path, black_cmd)
    black_result = run_command(black_cmd)
    if black_result.returncode != 0:
        raise BlackCheckError("black check failed")
    click.echo(click.style("black check completed", fg="green"))


@click.command()
@click.pass_context
@click.option(
    "--check",
    help="Don't apply formatting, just check if formatting is needed.",
    is_flag=True,
)
def formatting(ctx: click.Context, check: bool) -> None:
    """
    Run suite of Python code formatting.

    The suite currently comprises "isort and "black". isort is run before black
    to resolve cases where isort and black compete over formatting changes.
    """
    try:
        ctx.ensure_object(dict)
        command_state: CommandState = ctx.obj["command_state"]
        if not check:
            _apply_formatting(command_state.venv_path)
        else:
            _check_formatting(command_state.venv_path)
        click.echo(click.style("formatting completed", fg="green"))
    except FormattingError as e:
        report_console_error(str(e))
        sys.exit(ExitState.FORMATTING_FAILED.value)
    except BlackCheckError as e:
        report_console_error(str(e))
        sys.exit(ExitState.BLACK_CHECK_FAILED.value)
    except IsortCheckError as e:
        report_console_error(str(e))
        sys.exit(ExitState.ISORT_CHECK_FAILED.value)
    except Exception:
        message = "Unexpected error. Check log for details."
        log.exception(message)
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
