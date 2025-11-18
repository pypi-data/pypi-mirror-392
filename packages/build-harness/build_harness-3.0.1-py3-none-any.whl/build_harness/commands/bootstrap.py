#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Initialize a new project from a template."""

import logging
import pathlib
import sys

import click
from cookiecutter.main import cookiecutter  # type: ignore

from build_harness._utility import report_console_error

from .state import ExitState

log = logging.getLogger(__name__)

VALID_CI_CHOICES = ["gitlabci"]
VALID_PACKAGER_CHOICES = ["flit"]


@click.command()
@click.pass_context
@click.argument(
    "project_name",
    type=str,
)
@click.option(
    "--ci",
    default=VALID_CI_CHOICES[0],
    help="Select CI pipeline file(s) to be generated.",
    type=click.Choice(VALID_CI_CHOICES),
)
@click.option(
    "--default-branch",
    default="main",
    help="Select CI pipeline file(s) to be generated.",
    type=str,
)
@click.option(
    "--disable-dependencies",
    default=False,
    help="Disable build harness dependency installation (development only). If "
    "disabled it is assumed the user has pre-installed the necessary "
    "dependencies in the correct location.",
    is_flag=True,
)
@click.option(
    "--force",
    default=False,
    help="Write over any existing files.",
    is_flag=True,
)
@click.option(
    "--packager",
    default=VALID_PACKAGER_CHOICES[0],
    help="Select Python packaging utility to be used.",
    type=click.Choice(VALID_PACKAGER_CHOICES),
)
def bootstrap(
    ctx: click.Context,
    ci: str,
    default_branch: str,
    disable_dependencies: bool,
    force: bool,
    packager: str,
    project_name: str,
) -> None:
    """
    Initialize a new Python project from a template.

    The new project includes initial unit tests, coverage analysis, working CI
    pipeline, packaging and publishing to pypi.org.
    """
    try:
        template_dir = pathlib.Path(__file__).parent / "../templates"

        context_configuration = {
            "default_branch": default_branch,
            "packaging_provider": packager,
            "pipeline_provider": ci,
            "project_name": project_name,
            # Regular users should not need this option, but it is needed for
            # integration tests to acquire the correct build_harness version for
            # testing.
            "disable_bh_dependencies": disable_dependencies,
        }
        cookiecutter(
            str(template_dir),
            extra_context=context_configuration,
            no_input=True,
            replay=False,
            # NOTE: require overwrite_if_exists==True because project directory
            #       is populated with .venv before cookiecutter is run.
            #       Otherwise cookiecutter will fail.
            overwrite_if_exists=True,
            output_dir=str(pathlib.Path.cwd()),
        )
    except Exception as e:
        message = "Unexpected error. Check log for details."
        log.exception(message)
        log.error(str(e))
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
