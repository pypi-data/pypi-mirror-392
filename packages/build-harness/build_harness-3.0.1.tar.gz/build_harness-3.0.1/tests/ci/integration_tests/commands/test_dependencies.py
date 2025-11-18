#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib
import tempfile

from build_harness.commands.dependencies import _check_virtual_environment


class TestCheckVirtualEnvironment:
    def test_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            mock_project_dir = pathlib.Path(directory)

            venv_path = _check_virtual_environment(mock_project_dir)

            assert venv_path.is_dir()
