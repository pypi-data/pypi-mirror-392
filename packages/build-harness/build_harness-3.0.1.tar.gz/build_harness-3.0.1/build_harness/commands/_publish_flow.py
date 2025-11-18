#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#


"""Publish flow command entry point."""

import logging
import pathlib
import sys
import typing

import click
from click_logging_config.parameters import (
    LoggingConfiguration,
    logging_parameters,
)

from build_harness._utility import report_console_error
from build_harness._version import __version__, acquire_version
from build_harness.tools.git import (
    DEFAULT_DEFAULT_BRANCH_NAME,
    GitNotFoundError,
    GitRepoError,
    get_tag_data,
    validate_git,
)

from ._declarations import (
    DEFAULT_CONSOLE_LOGGING_ENABLED,
    DEFAULT_FILE_LOGGING_ENABLED,
    DEFAULT_PROJECT_PATH,
    PublishOptions,
)
from ._release_id import InvalidReleaseId, validate_release_id
from .state import CommandState, ExitState

log = logging.getLogger(__name__)

DEFAULT_PUBLISHFLOW_LOGCONFIG = LoggingConfiguration.parse_obj(
    {
        "enable_file_logging": DEFAULT_FILE_LOGGING_ENABLED,
        "enable_console_logging": DEFAULT_CONSOLE_LOGGING_ENABLED,
        "file_logging": {"log_file_path": pathlib.Path("publish_flow.log")},
        "log_level": "debug",
    }
)

VALID_PR_IDENTIFIERS = {
    # Gitlab-CI
    "merge_request_event",
}


@click.command()
@click.version_option(version=acquire_version())
@click.option(
    "--default-branch",
    default=DEFAULT_DEFAULT_BRANCH_NAME,
    help="Git default/main branch name.",
    show_default=True,
    type=str,
)
@click.option(
    "--disable-pr-publish",
    default=None,
    help="""Disable pull/merge request pipeline publishing artifacts.

For Gitlab-CI TEXT must be the value of CI_PIPELINE_SOURCE variable.

[default: enabled - PR/MR pipeline behaves the same as feature branch
pipeline]""",
    type=str,
)
@click.option(
    "--git",
    default=None,
    help="Git executable. [default: users PATH]",
    type=str,
)
@click.option(
    "--project",
    default=DEFAULT_PROJECT_PATH,
    help="Git project directory.",
    show_default=True,
    type=str,
)
@click.option(
    "--publish-nonrelease",
    default=False,
    help="Publish on untagged non-releases.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "--publish-prerelease",
    default=False,
    help="Publish on a semantic version pre-release tag.",
    is_flag=True,
    show_default=True,
)
@logging_parameters(DEFAULT_PUBLISHFLOW_LOGCONFIG)
def publish_flow_main(
    default_branch: str,
    disable_pr_publish: typing.Optional[str],
    git: typing.Optional[str],
    project: str,
    publish_nonrelease: bool,
    publish_prerelease: bool,
) -> None:
    """
    Determine whether to publish from git tag and commit history.

    By default, if HEAD commit is tagged with a semantic version release then
    publish is activated. Otherwise publishing is deactivated.

    The utility emits the ``--publish`` or ``--no-publish`` option to be
    consumed by the ``build-harness publish`` subcommand.
    """
    try:
        state = CommandState(
            project_path=pathlib.Path(project),
            venv_path=pathlib.Path(sys.argv[0]).parent.absolute(),
        )
        log.info(f"build harness version, {__version__}")

        validate_git(git)

        tag_data = get_tag_data(state.project_path, default_branch)
        tag_version = validate_release_id(tag_data.tag)
        publish_result = PublishOptions.test.name
        if (
            (tag_data.offset and publish_nonrelease)
            or (
                tag_version.is_prerelease
                and (not tag_data.offset)
                and (publish_prerelease or publish_nonrelease)
            )
            or ((not tag_version.is_prerelease) and (not tag_data.offset))
        ) and (not tag_version.local):
            publish_result = PublishOptions.yes.name
        elif (tag_version.local and tag_version.local.startswith("dryrun")) or (
            disable_pr_publish and (disable_pr_publish in VALID_PR_IDENTIFIERS)
        ):
            publish_result = PublishOptions.dryrun.name

        click.echo(publish_result, err=False, nl=False)
    except InvalidReleaseId as e:
        report_console_error(str(e))
        sys.exit(ExitState.BAD_VERSION.value)
    except GitRepoError as e:
        report_console_error(str(e))
        sys.exit(ExitState.BAD_REPO.value)
    except GitNotFoundError as e:
        report_console_error(str(e))
        click.echo("Git must be installed and configured to use this utility.")
        click.echo("In Linux, something like this is necessary:")
        click.echo("    sudo apt install -y git || sudo yum install git")
        click.echo('    git config user.name "Your Name"')
        click.echo('    git config user.email "you@example.com"')
        sys.exit(ExitState.BAD_GIT_EXE.value)
    except Exception as e:
        message = "Unexpected error. Check log for details."
        log.exception(str(e))
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
