#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

from build_harness.entrypoint import build_harness_entry, release_flow_entry


def test_build_harness_entry(mocker):
    mock_main = mocker.patch("build_harness.entrypoint.main")

    build_harness_entry()

    mock_main.assert_called_once()


def test_release_flow_entry(mocker):
    mock_main = mocker.patch("build_harness.entrypoint.release_flow_main")

    release_flow_entry()

    mock_main.assert_called_once()
