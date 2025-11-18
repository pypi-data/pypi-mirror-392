#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

from build_harness import __version__
from build_harness.commands import main
from tests.ci.support.click_runner import click_runner  # noqa: F401


def test_main(click_runner):
    """Invoking without subcommand should fail (& generate help text)."""
    result = click_runner.invoke(main, [])

    assert result.exit_code == 2


def test_help(click_runner):
    result = click_runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Usage: main [OPTIONS] COMMAND [ARGS]" in result.output


def test_version(click_runner):
    result = click_runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output
