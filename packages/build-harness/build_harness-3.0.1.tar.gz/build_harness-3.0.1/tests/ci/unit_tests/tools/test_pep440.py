#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

from build_harness.tools import Pep440Patterns


class TestPep440:
    def test_regex(self):
        under_test = Pep440Patterns.SPECIFIER_PATTERN

        result = under_test.search("empty_specifier")
        assert result is not None

        result = under_test.search("multiple_specifiers >=2.2, <3.0")
        assert result is not None
        assert result.group("specifier_sets") == ">=2.2, <3.0"

        result = under_test.search("missing_whitespace>=2.2,<3.0")
        assert result is not None
        assert result.group("specifier_sets") == ">=2.2,<3.0"
