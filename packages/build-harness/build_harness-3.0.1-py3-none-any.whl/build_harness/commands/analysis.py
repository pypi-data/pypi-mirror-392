#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Static analysis subcommand implementation."""

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
from build_harness.project import acquire_source_dir

from .code_style import FormattingError, _apply_formatting
from .state import CommandState, ExitState

log = logging.getLogger(__name__)


FLAKE8_FORMAT_CMD: CommandArgs = ["flake8", "."]
MYPY_FORMAT_CMD: CommandArgs = ["mypy", "--show-error-codes", "."]

VALID_ANALYSIS_OPTIONS = [
    "all",
    "flake8",
    "mypy",
]


class StaticAnalysisError(Exception):
    """Problem occurred during static analysis."""


class Flake8Error(StaticAnalysisError):
    """Problem occurred with flake8 analysis."""


class MypyError(StaticAnalysisError):
    """Problem occurred with mypy analysis."""


def _run_flake8(source_path: pathlib.Path, venv_path: pathlib.Path) -> None:
    """
    Run flake8 analysis on the specified source directory.

    Args:
        source_path: Path to project source directory.
        venv_path: Path to Python virtual environment.

    Raises:
        StaticAnalysisError: If flake8 analysis fails.
    """
    click.echo("flake8 analysis...")
    FLAKE8_FORMAT_CMD[0] = command_path(venv_path, FLAKE8_FORMAT_CMD)
    FLAKE8_FORMAT_CMD[-1] = str(source_path)
    result = run_command(FLAKE8_FORMAT_CMD)

    if result.returncode != 0:
        raise Flake8Error("flake8 analysis failed")
    click.echo(click.style("flake8 analysis completed", fg="green"))


def _run_mypy(source_path: pathlib.Path, venv_path: pathlib.Path) -> None:
    """
    Run mypy analysis on the specified source directory.

    Args:
        source_path: Path to project source directory.
        venv_path: Path to Python virtual environment.

    Raises:
        StaticAnalysisError: If mypy analysis fails.
    """
    click.echo("mypy analysis...")
    MYPY_FORMAT_CMD[0] = command_path(venv_path, MYPY_FORMAT_CMD)
    MYPY_FORMAT_CMD[-1] = str(source_path)
    result = run_command(MYPY_FORMAT_CMD)

    if result.returncode != 0:
        raise MypyError("mypy analysis failed")
    click.echo(click.style("mypy analysis completed", fg="green"))


def _apply_analysis(
    analysis_type: str, project_path: pathlib.Path, venv_path: pathlib.Path
) -> None:
    """
    Apply the specified analysis.

    Args:
        project_path: Path to project root directory.
        venv_path: Path to Python virtual environment.
    """
    source_dir = acquire_source_dir(project_path)

    analysis_methods = {
        "flake8": _run_flake8,
        "mypy": _run_mypy,
    }
    if analysis_type != "all":
        analysis_methods[analysis_type](project_path / source_dir, venv_path)
    else:
        for this_method in [y for x, y in analysis_methods.items()]:
            this_method(project_path / source_dir, venv_path)


@click.command()
@click.option(
    "--analysis",
    default="all",
    help="Analysis type to apply (default all)",
    type=click.Choice(VALID_ANALYSIS_OPTIONS, case_sensitive=True),
)
@click.pass_context
def static_analysis(ctx: click.Context, analysis: str) -> None:
    """
    Run suite of Python static analysis.

    The suite currently comprises "flake8" and "mypy". Formatting is run before
    the static analysis to eliminate formatting complaints from static analysis
    tools.
    """
    try:
        ctx.ensure_object(dict)
        command_state: CommandState = ctx.obj["command_state"]

        _apply_formatting(command_state.venv_path)
        _apply_analysis(
            analysis, command_state.project_path, command_state.venv_path
        )
    except FormattingError as e:
        report_console_error(str(e))
        sys.exit(ExitState.FORMATTING_FAILED.value)
    except Flake8Error as e:
        report_console_error(str(e))
        sys.exit(ExitState.FLAKE8_FAILED.value)
    except MypyError as e:
        report_console_error(str(e))
        sys.exit(ExitState.MYPY_FAILED.value)
    except Exception:
        message = "Unexpected error. Check log for details."
        log.exception(message)
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
