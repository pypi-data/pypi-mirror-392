#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""CLI command processing for ``build-harness`` command."""

import logging
import pathlib
import sys

import click
from click_logging_config.parameters import logging_parameters

from build_harness._version import __version__, acquire_version

from ._declarations import DEFAULT_BUILDHARNESS_LOGCONFIG, DEFAULT_PROJECT_PATH
from .analysis import static_analysis
from .bdd import bdd_acceptance_command
from .bootstrap import bootstrap
from .code_style import formatting
from .dependencies import install
from .publishing import publish
from .state import CommandState
from .unit_tests import unit_test
from .wheel import package

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.version_option(version=acquire_version())
@logging_parameters(DEFAULT_BUILDHARNESS_LOGCONFIG)
def main(
    ctx: click.Context,
) -> None:
    """Build harness group."""
    ctx.ensure_object(dict)
    ctx.obj["command_state"] = CommandState(
        project_path=pathlib.Path(DEFAULT_PROJECT_PATH),
        venv_path=pathlib.Path(sys.argv[0]).parent.absolute(),
    )
    log.info(f"build harness version, {__version__}")


main.add_command(bdd_acceptance_command, name="acceptance")
main.add_command(bootstrap, name="bootstrap")
main.add_command(formatting, name="formatting")
main.add_command(install, name="install")
main.add_command(package, name="package")
main.add_command(publish, name="publish")
main.add_command(static_analysis, name="static-analysis")
main.add_command(unit_test, name="unit-test")
