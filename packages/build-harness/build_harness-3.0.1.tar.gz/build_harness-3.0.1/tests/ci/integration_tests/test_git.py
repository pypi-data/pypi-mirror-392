#
#  Copyright (c) 2022 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

from build_harness.tools.git import _validate_git_version


class TestValidateGitVersion:
    def test_clean(self):
        # WARNING: assumes the test run context includes a valid git release
        # (should be true for developers and CI).
        _validate_git_version()
