#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import os
import pathlib

from behave import then, when

from build_harness._utility import run_command

from .support import build_harness_context, chdir_project_dir, create_venv

DEBUG_INSTALL = False


@when("the build harness command is run")
def step_impl(context):
    pre_step_actions = None
    if hasattr(context, "pre_step_actions"):
        pre_step_actions = context.pre_step_actions
    release_id = "0.0.0"
    if hasattr(context, "release_id"):
        release_id = context.release_id

    test_install = False
    if hasattr(context, "test_install"):
        test_install = True

    with build_harness_context(
        context.create_pyproject,
        release_id,
        context.existing_project_venv,
        debug_install=DEBUG_INSTALL,
        pre_step_actions=pre_step_actions,
    ) as (
        temporary_dir,
        this_bh_command,
    ):
        mock_project = pathlib.Path(temporary_dir)
        print(f"project dir, {mock_project}")
        print(f"cwd before chdir, {os.getcwd()}")
        with chdir_project_dir(mock_project):
            print(f"cwd after chdir, {os.getcwd()}")

            this_command = [str(this_bh_command)] + context.given_arguments
            if hasattr(context, "release_id"):
                this_command += ["--release-id", release_id]
            result = run_command(
                this_command,
                capture_output=True,
                text=True,
                universal_newlines=True,
            )

            print(result.stdout)
            print(result.stderr)

            context.run_result = result

            context.mock_project = mock_project
            context.project_dir_list = list(mock_project.iterdir())
            dist_dir = mock_project / "dist"
            context.dist_dir_list = (
                list(dist_dir.iterdir()) if dist_dir.is_dir() else list()
            )

            if hasattr(context, "post_step_actions"):
                context.post_step_actions(context, result, mock_project)

            if test_install:
                tmpv_pip = create_venv(mock_project / "tmpv")
                this_command = [
                    str(tmpv_pip),
                    "install",
                    str(context.dist_dir_list[1]),
                ]
                result = run_command(
                    this_command,
                    capture_output=True,
                    text=True,
                    universal_newlines=True,
                )

                print(result.stdout)
                print(result.stderr)

                result = run_command(
                    [tmpv_pip, "list"],
                    capture_output=True,
                    text=True,
                    universal_newlines=True,
                )

                context.pip_list = result.stdout


@then("the utility exits clean")
def step_impl(context):
    print(context.run_result.returncode)
    assert context.run_result.returncode == 0


@then("the utility exits dirty")
def step_impl(context):
    print(context.run_result.returncode)
    assert context.run_result.returncode != 0
