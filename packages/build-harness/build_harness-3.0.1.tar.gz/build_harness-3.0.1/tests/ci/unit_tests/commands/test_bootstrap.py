#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import typing

import pytest

from build_harness.commands import ExitState, main
from tests.ci.support.click_runner import click_runner  # noqa: F401


@pytest.fixture
def run_bootstrap(click_runner, mocker):
    def _apply(command_arguments: typing.List[str], this_runner):
        mock_cookiecutter = mocker.patch(
            "build_harness.commands.bootstrap.cookiecutter"
        )
        arguments = ["bootstrap"] + command_arguments
        result = this_runner.invoke(main, arguments)

        return result, mock_cookiecutter

    return _apply


class TestBootstrap:
    def test_default(self, click_runner, run_bootstrap, mocker):
        result, mock_cookiecutter = run_bootstrap(
            ["my_new_project"], click_runner
        )

        assert result.exit_code == 0
        mock_cookiecutter.assert_called_once_with(
            mocker.ANY,
            extra_context={
                "default_branch": "main",
                "disable_bh_dependencies": False,
                "packaging_provider": "flit",
                "pipeline_provider": "gitlabci",
                "project_name": "my_new_project",
            },
            no_input=True,
            replay=False,
            overwrite_if_exists=True,
            output_dir=mocker.ANY,
        )

    def test_ci(self, click_runner, run_bootstrap, mocker):
        result, mock_cookiecutter = run_bootstrap(
            ["my_new_project", "--ci", "gitlabci"], click_runner
        )

        assert result.exit_code == 0
        mock_cookiecutter.assert_called_once_with(
            mocker.ANY,
            extra_context={
                "default_branch": "main",
                "disable_bh_dependencies": False,
                "packaging_provider": "flit",
                "pipeline_provider": "gitlabci",
                "project_name": "my_new_project",
            },
            no_input=True,
            replay=False,
            overwrite_if_exists=True,
            output_dir=mocker.ANY,
        )

    def test_packager(self, click_runner, run_bootstrap, mocker):
        result, mock_cookiecutter = run_bootstrap(
            ["my_new_project", "--packager", "flit"], click_runner
        )

        assert result.exit_code == 0
        mock_cookiecutter.assert_called_once_with(
            mocker.ANY,
            extra_context={
                "default_branch": "main",
                "disable_bh_dependencies": False,
                "packaging_provider": "flit",
                "pipeline_provider": "gitlabci",
                "project_name": "my_new_project",
            },
            no_input=True,
            replay=False,
            overwrite_if_exists=True,
            output_dir=mocker.ANY,
        )

    def test_default_branch(self, click_runner, run_bootstrap, mocker):
        result, mock_cookiecutter = run_bootstrap(
            ["my_new_project", "--default-branch", "fancy"], click_runner
        )

        assert result.exit_code == 0
        mock_cookiecutter.assert_called_once_with(
            mocker.ANY,
            extra_context={
                "default_branch": "fancy",
                "disable_bh_dependencies": False,
                "packaging_provider": "flit",
                "pipeline_provider": "gitlabci",
                "project_name": "my_new_project",
            },
            no_input=True,
            replay=False,
            overwrite_if_exists=True,
            output_dir=mocker.ANY,
        )

    def test_force(self, click_runner, run_bootstrap, mocker):
        result, mock_cookiecutter = run_bootstrap(
            ["my_new_project", "--force"], click_runner
        )

        assert result.exit_code == 0
        mock_cookiecutter.assert_called_once_with(
            mocker.ANY,
            extra_context={
                "default_branch": "main",
                "disable_bh_dependencies": False,
                "packaging_provider": "flit",
                "pipeline_provider": "gitlabci",
                "project_name": "my_new_project",
            },
            no_input=True,
            replay=False,
            overwrite_if_exists=True,
            output_dir=mocker.ANY,
        )

    def test_bad_ci_choice_error(self, click_runner, mocker):
        mocker.patch("build_harness.commands.bootstrap.cookiecutter")
        result = click_runner.invoke(
            main, ["bootstrap", "new_project", "--ci", "bad_choice"]
        )

        assert result.exit_code == 2

    def test_bad_packager_choice_error(self, click_runner, mocker):
        mocker.patch("build_harness.commands.bootstrap.cookiecutter")
        result = click_runner.invoke(
            main, ["bootstrap", "new_project", "--packager", "bad_choice"]
        )

        assert result.exit_code == 2

    def test_unknown_error(self, click_runner, mocker):
        mocker.patch(
            "build_harness.commands.bootstrap.cookiecutter",
            side_effect=RuntimeError(),
        )
        result = click_runner.invoke(main, ["bootstrap", "new_project"])

        assert result.exit_code == ExitState.UNKNOWN_ERROR.value
