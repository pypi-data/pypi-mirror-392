#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Package generation subcommand implementation."""

import copy
import logging
import pathlib
import sys
import typing

import click
import git  # type: ignore

from build_harness._utility import (
    CommandArgs,
    command_path,
    report_console_error,
    run_command,
)
from build_harness.project import acquire_source_dir

from ._release_id import validate_release_id
from .state import CommandState, ExitState

log = logging.getLogger(__name__)

DEFAULT_VERSION_FILE = "VERSION"

FLIT_BUILD_CMD: CommandArgs = ["flit", "build"]


class PackagingError(Exception):
    """Problem occurred during packaging."""


class ReleaseEmptyOption(click.Option):
    """Optional release id with empty value."""

    empty_value = True


T = typing.TypeVar("T", bound="ReleaseValueOption")


class ReleaseValueOption(click.Option):
    """Fix the help for the _set suffix."""

    def get_help_record(self: T, ctx: click.Context) -> typing.Tuple[str, str]:
        """Customize help text."""
        help = typing.cast(
            typing.Tuple[str, str],
            super(ReleaseValueOption, self).get_help_record(ctx),
        )
        return (help[0].replace("_set ", " "),) + help[1:]


def _apply_release_id(release_id: str, version_file_path: pathlib.Path) -> None:
    """
    Apply the release id to the project source package directory.

    Args:
        release_id: Release id to be applied to source directory.
        project_path: Path to project directory.
    """
    validate_release_id(release_id)

    log.info(
        "Saving version file, {0} ({1})".format(version_file_path, release_id)
    )
    with version_file_path.open(mode="w") as f:
        f.write(release_id)

    try:
        repo = git.Repo(str(version_file_path.parent / ".."))
        repo.index.add([str(version_file_path)])
        repo.index.commit(str(version_file_path))
    except git.InvalidGitRepositoryError as e:
        # log the warning and ignore the error
        log.warning(str(e))


def _build_flit_package(venv_path: pathlib.Path) -> None:
    """
    Build packages using flit.

    Args:
        venv_path: Path to Python virtual environment.

    Raises:
        PackagingError: If package build exits non-zero.
    """
    flit_cmd = copy.deepcopy(FLIT_BUILD_CMD)
    flit_cmd[0] = command_path(venv_path, flit_cmd)
    result = run_command(flit_cmd)

    if any(x != 0 for x in [result.returncode]):
        raise PackagingError("flit failed during package build.")


@click.command()
@click.pass_context
@click.option(
    "--release-id",
    default=None,
    help="PEP-440 release id to apply to package. [default: do nothing]",
    type=str,
)
def package(ctx: click.Context, release_id: typing.Optional[str]) -> None:
    """Build wheel, sdist packages."""
    try:
        ctx.ensure_object(dict)
        command_state: CommandState = ctx.obj["command_state"]

        source_dir = pathlib.Path(
            acquire_source_dir(command_state.project_path)
        )
        version_file_path = source_dir / DEFAULT_VERSION_FILE

        try:
            if release_id:
                _apply_release_id(release_id, version_file_path)

            _build_flit_package(command_state.venv_path)
        except PackagingError as e:
            message = str(e)
            log.error(message)
            report_console_error(message)
            sys.exit(ExitState.PACKAGING_FAILED.value)
        finally:
            try:
                # NOTE: Can't use `missing_ok` option for Python <3.8
                version_file_path.unlink()
            except FileNotFoundError:
                # log the exception, but swallow it.
                log.info(f"Version file does not exist, {version_file_path}")
    except Exception:
        message = "Unexpected error. Check log for details."
        log.exception(message)
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
