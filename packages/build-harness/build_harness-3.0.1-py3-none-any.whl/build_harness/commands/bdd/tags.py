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

from build_harness._utility import command_path, run_command

log = logging.getLogger(__name__)


def _summarize_tags(venv_path: pathlib.Path) -> None:
    behave_command = ["behave", "--format", "tags.location", "features"]
    behave_command[0] = command_path(venv_path, behave_command)
    # ignore errors from the snippets command
    run_command(behave_command)
