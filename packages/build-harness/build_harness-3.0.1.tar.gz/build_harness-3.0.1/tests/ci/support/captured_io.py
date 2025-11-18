#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import contextlib
import dataclasses
import io
import sys
import typing


@dataclasses.dataclass
class StdIo:
    err: io.StringIO
    out: io.StringIO


@contextlib.contextmanager
def capture_io() -> typing.ContextManager[StdIo]:
    new = StdIo(err=io.StringIO(), out=io.StringIO())
    with contextlib.redirect_stderr(new.err), contextlib.redirect_stdout(
        new.out
    ):
        yield new
