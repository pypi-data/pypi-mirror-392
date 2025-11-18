#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""PEP-503 related functions."""

import re


def pep503_normalize(name: str) -> str:
    """
    Normalize a package name per PEP-503.

    Assumes the name is compliant with PEP-426.

    https://www.python.org/dev/peps/pep-0503/#normalized-names
    https://www.python.org/dev/peps/pep-0426/

    Args:
        name: PEP-426 compliant package name.

    Returns:
        PEP-503 normalized name.
    """
    return re.sub(r"[-_.]+", "-", name).lower()
