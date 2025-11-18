#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib
import re

from behave import given, then

from .support import create_mock_pyproject, create_source_dir

DEBUG_INSTALL = False


def package_post_step_actions(context, result, mock_project):
    if result.returncode == 0:
        whl_package_dir = mock_project / "dist" / ""
        context.whl_packages = list(whl_package_dir.iterdir())


@then("the wheel package is created")
def step_impl(context):
    expected_package = "some_module-0.0.0-py2.py3-none-any.whl"
    search_result = [expected_package in str(x) for x in context.whl_packages]
    if not any(search_result):
        print(context.whl_packages)
    assert any(search_result)


def _create_bad_pyproject(file_path: pathlib.Path):
    with file_path.open(mode="w") as f:
        f.write(
            """[build-system]
requires = ["something_else >=2,<3"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
module = "some_module"
author = "Some Name"
author-email = "name@somewhere.com"
"""
        )


@given("a flit project directory to be packaged")
def step_impl(context):
    context.existing_project_venv = False
    context.create_pyproject = create_mock_pyproject
    context.given_arguments = ["package"]
    context.pre_step_actions = create_source_dir
    context.post_step_actions = package_post_step_actions
    context.packager = "flit"


@given("a project directory using a non-supported packaging utility")
def step_impl(context):
    context.existing_project_venv = False
    context.create_pyproject = create_mock_pyproject
    context.pre_step_actions = create_source_dir
    context.packager = "something_else"
    context.given_arguments = ["package"]
    context.post_step_actions = package_post_step_actions


@then("the correct packaging tool cannot be identified")
def step_impl(context):
    assert "" in context.run_result.output


@given("a PEP440 compliant release id")
def step_impl(context):
    context.release_id = "3.1.4.dev123"
    context.test_install = True


@then("the wheel package file identifies itself with the release id")
def step_impl(context):
    print(context.dist_dir_list)
    assert any(
        [
            re.search(r"dist/some_module[_\-]3\.1\.4\.dev123-py.+whl", str(x))
            is not None
            for x in context.dist_dir_list
        ]
    )


@then("when installed the package identifies itself with the release id")
def step_impl(context):
    print(context.pip_list)
    assert (
        re.search(r"some_module\s+3\.1\.4\.dev123", context.pip_list)
        is not None
    )


@given("no release id specified")
def step_impl(context):
    assert not hasattr(context, "release_id")


@then("the wheel package file identifies itself with the default release id")
def step_impl(context):
    assert any(
        [
            re.search(r"dist/some_module[_\-]0\.0\.0-py.+whl", str(x))
            is not None
            for x in context.dist_dir_list
        ]
    )
