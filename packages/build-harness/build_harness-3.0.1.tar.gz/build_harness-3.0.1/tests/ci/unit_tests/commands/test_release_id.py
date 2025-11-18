#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pytest
from parver import ParseError

from build_harness.commands._release_id import (
    InvalidReleaseId,
    validate_release_id,
)


def test_public_release():
    expected_release = "3.1.4"
    result = validate_release_id(expected_release)

    assert result.public == expected_release
    assert result.post is None


def test_replace_post():
    expected_release = "3.1.4"
    result = validate_release_id(expected_release)

    assert result.public == expected_release
    assert result.post is None

    v = result.replace(post=5)
    assert v.post == 5


def test_post_release():
    expected_release = "3.1.4.post11"
    result = validate_release_id(expected_release)

    assert result.public == expected_release
    assert result.post == 11


def test_local_dryrun():
    expected_release = "3.1.4.post11+dryrun"
    result = validate_release_id(expected_release)

    assert result.public == "3.1.4.post11"
    assert result.post == 11
    assert result.local == "dryrun"
    assert str(result) == expected_release


def test_dev_release():
    expected_release = "3.1.4.post11.dev456"
    result = validate_release_id(expected_release)

    assert result.public == "3.1.4.post11.dev456"
    assert result.post == 11
    assert result.dev == 456
    assert str(result) == expected_release


def test_failed_parse_raises(mocker):
    expected_release = "bad_tag"

    mocker.patch(
        "build_harness.commands._release_id.parver.Version.parse",
        side_effect=ParseError("some error"),
    )

    with pytest.raises(
        InvalidReleaseId, match=r"^Tags must be PEP-440 compliant"
    ):
        validate_release_id(expected_release)
