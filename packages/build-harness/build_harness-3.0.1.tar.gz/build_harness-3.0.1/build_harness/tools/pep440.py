#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""PEP-440 regular expression patterns."""

import re

from .pep426 import Pep426Patterns


class Pep440Patterns:
    """PEP-440 regular expression patterns."""

    VALID_SPECIFIERS = r"(==|~=|>=|<=|!=|>|<)"
    VALID_VERSION_CHARACTERS = r"[0-9ab.\-_!postdevrc]+"
    SPECIFIER_SET_PATTERN = r"({0}\s*{1})".format(
        VALID_SPECIFIERS, VALID_VERSION_CHARACTERS
    )

    SPECIFIER_PATTERN = re.compile(
        r"^\s*{0}(\s*(?P<specifier_sets>({1},)*(\s*{1})?))?".format(
            Pep426Patterns.UNNORMALIZED_PACKAGE_NAME, SPECIFIER_SET_PATTERN
        )
    )
