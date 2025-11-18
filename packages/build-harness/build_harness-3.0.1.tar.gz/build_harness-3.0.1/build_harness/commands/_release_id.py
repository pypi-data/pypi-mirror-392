#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Actions relating to release ids."""

import logging

import parver  # type: ignore

log = logging.getLogger(__name__)


class InvalidReleaseId(Exception):
    """Parsed release ID is not valid PEP-440."""


def validate_release_id(release_id: str) -> parver.Version:
    """
    Validate release id according to PEP-440.

    https://www.python.org/dev/peps/pep-0440/

    Args:
        release_id: Release id to validate.

    Raises:
        InvalidReleaseId: If release id is not valid PEP-440.
    """
    try:
        return parver.Version.parse(release_id)
    except parver.ParseError as e:
        log.debug("handling parver.ParseError, {0}".format(str(e)))
        message = "Tags must be PEP-440 compliant, {0}".format(release_id)
        raise InvalidReleaseId(message) from e
