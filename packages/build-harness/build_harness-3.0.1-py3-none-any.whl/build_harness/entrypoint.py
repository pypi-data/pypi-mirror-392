#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Define flit entry points."""

from .commands import main, publish_flow_main, release_flow_main


def build_harness_entry() -> None:
    """Flit entry point to ``build-harness`` command CLI argument parsing."""
    main()


def publish_flow_entry() -> None:
    """Flit entry point to ``publish-flow`` command CLI argument parsing."""
    publish_flow_main()


def release_flow_entry() -> None:
    """Flit entry point to ``release-flow`` command CLI argument parsing."""
    release_flow_main()
