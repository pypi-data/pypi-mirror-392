#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Package publish subcommand implementation."""

import copy
import io
import logging
import operator
import pathlib
import sys
import typing

import click

from build_harness._utility import (
    CommandArgs,
    command_path,
    report_console_error,
    run_command,
)

from ._declarations import PublishOptions
from .state import CommandState, ExitState

log = logging.getLogger(__name__)

PACKAGES_SPEC = ["dist/*.whl", "dist/*.tar.gz"]
TWINE_PUBLISH_CMD: CommandArgs = ["twine", "upload", "--non-interactive"]

PYPI_TEST_URL = "https://test.pypi.org/legacy/"


class PublishingError(Exception):
    """Problem occurred during publishing."""


def _obfuscate_password(password: str) -> str:
    """
    Obfuscate a password for debug logging.

    Args:
        password: Password text to be obfuscated.

    Returns:
        Last four characters of password, if possible. Completely obfuscated
        otherwise.
    """
    obfuscated_password: str = (
        "**{0}".format(password[-4:]) if len(password) > 4 else "*****"
    )

    return obfuscated_password


def _publish_packages(
    venv_path: pathlib.Path,
    publish_option: PublishOptions,
    password: typing.Optional[str],
    user: typing.Optional[str],
) -> None:
    """
    Publish sdist, wheel packages using twine.

    On dry run no publish occurs, but a summary of packages found that would
    have been published is printed to console.

    Args:
        venv_path: Path to Python virtual environment.
        publish_option: Publish option selected.
        password: Remote repository password.
        user: Remote repository username

    Raises:
        FileNotFoundError: if password file does not exist.
        PublishingError: If package publish exits non-zero.
    """
    this_command = copy.deepcopy(TWINE_PUBLISH_CMD)
    this_command[0] = command_path(venv_path, this_command)
    if publish_option == PublishOptions.test:
        this_command += ["--repository-url", PYPI_TEST_URL]
    this_command += PACKAGES_SPEC

    environment_variables = {}
    if user:
        log.debug("twine username, {0}".format(user))
        environment_variables["TWINE_USERNAME"] = user
    else:
        log.warning(
            "twine username not provided. assuming twine can figure it out..."
        )
    if password:
        obfuscated_password = _obfuscate_password(password)
        log.debug("twine password, {0}".format(obfuscated_password))
        environment_variables["TWINE_PASSWORD"] = password
    else:
        log.warning(
            "twine password not provided. assuming twine can figure it out..."
        )

    if publish_option in [PublishOptions.yes, PublishOptions.test]:
        log.debug("twine command run, {0}".format(str(this_command)))
        result = run_command(
            this_command,
            env=environment_variables,
            # suppress command logging in the run to protect accidental
            # exposure of credentials
            suppress_command_logging=True,
            suppress_argument_logging=True,
        )

        if any(x != 0 for x in [result.returncode]):
            raise PublishingError("twine failed during package publishing.")
    elif publish_option == PublishOptions.dryrun:
        this_command = ["twine", "check"] + PACKAGES_SPEC
        this_command[0] = command_path(venv_path, this_command)
        message = "Dry run, {0}".format(this_command)
        log.warning(message)
        click.echo(message)
        result = run_command(
            this_command,
            env=environment_variables,
            # suppress command logging in the run to protect accidental
            # exposure of credentials
            suppress_command_logging=True,
            suppress_argument_logging=True,
        )

        if any(x != 0 for x in [result.returncode]):
            raise PublishingError("twine failed during package check.")
    elif publish_option == PublishOptions.no:
        message = "Publish disabled"
        log.info(message)
        click.echo(message)
    else:
        # it shouldn't be possible to get here, unless PublishOptions is
        # changed in future in a way that the other conditionals don't cover.
        raise PublishingError("Unknown publish option")


@click.command()
@click.pass_context
@click.option(
    "--password",
    default=None,
    help="PEP-503 server login password",
    type=str,
)
@click.option(
    "--password-file",
    default=None,
    help="Path to file containing PEP-503 server login password",
    type=click.File(mode="r"),
)
@click.option(
    "--publish",
    default=PublishOptions.yes.name,
    help="""Control whether or not to publish package.

    yes - publish to pypi.org.
    no - do not publish or dryrun.
    dryrun - log the twine command to be run on publish without uploading
             anything.
    test - publish to pypi.org test server.
""",
    show_default=True,
    type=click.Choice(list(map(operator.attrgetter("name"), PublishOptions))),
)
@click.option(
    "--user",
    default=None,
    help="PEP-503 server login user name",
    type=str,
)
def publish(
    ctx: click.Context,
    password: typing.Optional[str],
    password_file: typing.Optional[io.FileIO],
    publish: str,
    user: typing.Optional[str],
) -> None:
    """Publish project artifacts."""
    try:
        ctx.ensure_object(dict)
        command_state: CommandState = ctx.obj["command_state"]

        this_password = None
        if password and password_file:
            raise PublishingError(
                "Cannot specify both `--password` and `--password-file` "
                "options."
            )
        elif password:
            log.debug(
                "password passed as CLI argument, {0}".format(
                    _obfuscate_password(password)
                )
            )
            this_password = password
        elif password_file:
            log.debug(
                "password specified in password file, {0!r}".format(
                    password_file.name
                )
            )
            this_password = typing.cast(str, password_file.read())
            if not this_password:
                raise PublishingError("Empty password file specified, {0}")
            log.debug(
                "password recovered from file, {0}".format(
                    _obfuscate_password(this_password)
                )
            )

        _publish_packages(
            command_state.venv_path,
            PublishOptions[publish],
            this_password,
            user,
        )
    except PublishingError as e:
        message = str(e)
        report_console_error(message)
        sys.exit(ExitState.PUBLISHING_FAILED.value)
    except Exception:
        message = "Unexpected error. Check log for details."
        log.exception(message)
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
