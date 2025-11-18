#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Python release specific imports."""

import sys

if ((sys.version_info[0] == 3) and (sys.version_info[1] >= 8)) or (
    sys.version_info[0] >= 4
):
    from typing import Literal, TypedDict  # noqa: F401
elif (sys.version_info[0] == 3) and (sys.version_info[1] in [7]):
    from typing_extensions import Literal, TypedDict  # noqa: F401
else:
    raise RuntimeError(
        "Unsupported Python version, {0}".format(sys.version_info)
    )
