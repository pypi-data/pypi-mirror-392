#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib

from behave import given, then

from build_harness._utility import run_command


def _create_mock_pyproject(file_path: pathlib.Path):
    with file_path.open(mode="w") as f:
        f.write(
            """
[tool.flit.metadata]
module = "some_module"

requires = [
    "requests",
]
"""
        )


def create_bad_pyproject(file_path: pathlib.Path):
    with file_path.open(mode="w") as f:
        f.write(
            """
[tool.flit.metadata]
module = "some_module"

requires = [
    "hopefullyreallyimprobablepackage",
]
"""
        )


def dependencies_post_step_actions(context, result, mock_project):
    if result.returncode == 0:
        project_pip_path = mock_project / ".venv" / "bin" / "pip"
        assert project_pip_path.parent.is_dir()
        assert project_pip_path.is_file()
        # only generate this data if the command succeeds.
        result = run_command(
            [str(project_pip_path), "list"],
            capture_output=True,
            text=True,
            universal_newlines=True,
        )
        context.venv_packages = result.stdout
    else:
        context.venv_err = result.stderr


@given("the virtual environment does not exist in the project directory")
def step_impl(context):
    context.existing_project_venv = False
    context.create_pyproject = _create_mock_pyproject
    context.given_arguments = ["install"]
    context.given_expected_package = "requests"
    context.post_step_actions = dependencies_post_step_actions


@given(
    "the project includes configuration that will cause the installation to fail"
)
def step_impl(context):
    context.existing_project_venv = False
    context.create_pyproject = create_bad_pyproject
    context.given_arguments = ["install"]
    context.post_step_actions = dependencies_post_step_actions


@given("the virtual environment already exists in the project directory")
def step_impl(context):
    context.existing_project_venv = True
    context.create_pyproject = _create_mock_pyproject
    context.given_arguments = ["install"]
    context.given_expected_package = "requests"
    context.post_step_actions = dependencies_post_step_actions


@then("installation error is reported to the console")
def step_impl(context):
    print(context.run_result.stdout)
    print(context.run_result.stderr)
    assert "Dependency installation failed" in context.run_result.stderr


@then("the virtual environment is created")
def step_impl(context):
    assert any([str(x).endswith(".venv") for x in context.project_dir_list])


@then(
    "the virtual environment is populated with necessary project dependencies"
)
def step_impl(context):
    print(context.given_expected_package)
    print(context.venv_packages)
    assert context.given_expected_package in context.venv_packages


@given("a virtual environment with the installed project dependencies")
def step_impl(context):
    context.existing_project_venv = True
    context.given_expected_package = "requests"
    context.post_step_actions = dependencies_post_step_actions


def create_requests_version(file_path: pathlib.Path, release_id: str):
    with file_path.open(mode="w") as f:
        f.write(
            """
[tool.flit.metadata]
module = "some_module"

requires = [
    "requests=={0}",
]
""".format(
                release_id
            )
        )


def dependency_change_actions(data: dict):
    project_dir = data["working_dir"]
    run_command(
        [str(project_dir / ".venv/bin/pip"), "install", "requests==2.17.2"],
        capture_output=True,
        text=True,
        universal_newlines=True,
    )


@given(
    "the project includes a dependency change in pyproject.toml that is not "
    "installed in the virtual environment"
)
def step_impl(context):
    context.create_pyproject = lambda x: create_requests_version(x, "2.24.0")
    context.pre_step_actions = dependency_change_actions
    context.post_step_actions = dependencies_post_step_actions


@given("the --check argument is added to the install command run")
def step_impl(context):
    context.given_arguments = ["install", "--check"]


@then("the dependency installation error is reported to the console")
def step_impl(context):
    print(context.run_result.stdout)
    print(context.run_result.stderr)
    assert (
        "Installed packages do not comply with declared project dependencies"
        in context.run_result.stderr
    )
