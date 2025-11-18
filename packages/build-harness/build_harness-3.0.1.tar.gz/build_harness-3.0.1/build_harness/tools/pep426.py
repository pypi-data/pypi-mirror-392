#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""PEP-426 related regular expression patterns."""


class Pep426Patterns:
    """PEP-426 regular expression patterns."""

    UNNORMALIZED_PACKAGE_NAME = r"(?P<package_name>[A-Za-z0-9\-_.]+)"
