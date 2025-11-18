#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pytest
from cookiecutter.main import cookiecutter

from tests.ci.support.project_context import (
    build_cookiecutter_context,
    make_project_venv,
    run_command,
)


class TestDefaultBranchCookiecutter:
    def test_default_branches(self):
        branches = ["main", "master"]

        with build_cookiecutter_context(enable_venv=False) as this_context:
            for this_branch in branches:
                project_name = this_branch
                context_configuration = {
                    "build_harness_version": "==0.0.0",
                    "default_branch": this_branch,
                    "disable_bh_dependencies": True,
                    "enable_venv": False,
                    "project_name": project_name,
                }

                project_dir = make_project_venv(
                    project_name,
                    this_context.temp_path,
                    enable_venv=False,
                )

                cookiecutter(
                    str(this_context.template_dir),
                    extra_context=context_configuration,
                    no_input=True,
                    replay=False,
                    overwrite_if_exists=True,
                    output_dir=this_context.temp_path,
                )

                response = run_command(
                    ["git", "-C", str(project_dir), "branch", "-l"],
                    capture_output=True,
                    text=True,
                )
                if response.returncode != 0:
                    pytest.fail("git command failed, {0}".format(this_branch))

                if "* {0}".format(this_branch) not in response.stdout:
                    pytest.fail(
                        "{0} branch not in repo, {1}".format(
                            this_branch, response.stdout
                        )
                    )
