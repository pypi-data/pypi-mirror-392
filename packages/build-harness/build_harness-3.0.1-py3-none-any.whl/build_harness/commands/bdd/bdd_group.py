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
import sys
import typing

import click

from build_harness._base_exception import BuildHarnessError
from build_harness._utility import report_console_error
from build_harness.commands.state import CommandState, ExitState

from .run_tests import AcceptanceTestsError, _run_bdd
from .snippets import _generate_snippets
from .tags import _summarize_tags

log = logging.getLogger(__name__)

DEFAULT_JUNITXML_DIR = "dist/behave"

VALID_BDD_RUN_TYPES = ["snippets", "tags", "tests"]


class AcceptanceError(BuildHarnessError):
    """Problem occurred during BDD run."""


@click.command()
@click.pass_context
@click.argument(
    "run_type",
    type=click.Choice(VALID_BDD_RUN_TYPES),
)
@click.option(
    "--junitxml",
    default=False,
    help="Enable junit XML test report.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "--junitxml-dir",
    default=None,
    help="Path to junit XML test report directory. [default: default auto file "
    "location when enabled]",
    metavar="FILE",
    type=str,
)
@click.option(
    "--tags",
    default=[None],
    help="Specify tags in Python behave style to select for in a run. "
    "[default: disabled]",
    metavar="BEHAVE_TAG",
    multiple=True,
    type=str,
)
def bdd_acceptance_command(
    ctx: click.Context,
    junitxml: bool,
    junitxml_dir: typing.Optional[str],
    run_type: str,
    tags: typing.Tuple[typing.Optional[str]],
) -> None:
    """
    BDD acceptance tests.

      snippets:  create snippets for BDD statement with no step implementation.
      tags:      show a table showing which feature files tags are used in.
      tests:     run acceptance tests.
    """
    try:
        ctx.ensure_object(dict)
        command_state: CommandState = ctx.obj["command_state"]

        if run_type == "snippets":
            _generate_snippets(command_state.venv_path)
        elif run_type == "tags":
            _summarize_tags(command_state.venv_path)
        elif run_type == "tests":
            if junitxml and junitxml_dir:
                junitxml_path = pathlib.Path(junitxml_dir)
            else:
                junitxml_path = pathlib.Path(DEFAULT_JUNITXML_DIR)
            _run_bdd(command_state.venv_path, junitxml, junitxml_path, tags)
        else:
            raise AcceptanceError(
                "Invalid acceptance run type, {0}".format(run_type)
            )
    except AcceptanceError as e:
        message = str(e)
        report_console_error(message)
        sys.exit(ExitState.ACCEPTANCE_RUN_FAILED.value)
    except AcceptanceTestsError as e:
        message = str(e)
        report_console_error(message)
        sys.exit(ExitState.ACCEPTANCE_TESTS_FAILED.value)
    except Exception:
        message = "Unexpected error. Check log for details."
        log.exception(message)
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
