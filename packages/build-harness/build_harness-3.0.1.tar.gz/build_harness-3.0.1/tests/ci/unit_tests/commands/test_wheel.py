#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib
import subprocess

import git
import pytest

from build_harness.commands import main
from build_harness.commands.wheel import _apply_release_id, _build_flit_package
from tests.ci.support.click_runner import click_runner  # noqa: F401


@pytest.fixture()
def mock_run(mock_sysargv, mocker):
    mock_pytest_result = mocker.create_autospec(subprocess.CompletedProcess)
    mock_pytest_result.returncode = 0
    mock_pytest_result.stdout = ""
    this_run = mocker.patch(
        "build_harness.commands.wheel.run_command",
        return_value=mock_pytest_result,
    )

    return this_run


class TestApplyReleaseId:
    def test_clean(self, mocker):
        mock_open = mocker.patch(
            "build_harness.commands.wheel.pathlib.Path.open"
        )
        mock_repo = mocker.patch(
            "build_harness.commands.wheel.git.Repo", autospec=True
        )

        mock_path = pathlib.Path("some/test_wheel_clean/path")
        mock_release = "1.2.3+abc3.14"

        _apply_release_id(mock_release, mock_path)

        mock_handle = mock_open.return_value.__enter__.return_value
        mock_handle.write.assert_called_once_with(mock_release)

        mock_repo.return_value.index.add.assert_called_once_with(
            [str(mock_path)]
        )
        mock_repo.return_value.index.commit.assert_called_once_with(
            str(mock_path)
        )

    def test_not_git_repo(self, mocker):
        mock_open = mocker.patch(
            "build_harness.commands.wheel.pathlib.Path.open"
        )
        mock_repo = mocker.patch(
            "build_harness.commands.wheel.git.Repo",
            autospec=True,
            side_effect=git.InvalidGitRepositoryError(),
        )

        mock_path = pathlib.Path("some/test_wheel_not_git_repo/path")
        mock_release = "1.2.3+abc3.14"

        _apply_release_id(mock_release, mock_path)

        mock_handle = mock_open.return_value.__enter__.return_value
        mock_handle.write.assert_called_once_with(mock_release)

        mock_repo.return_value.index.add.assert_not_called()
        mock_repo.return_value.index.commit.assert_not_called()


class TestPackageBuild:
    def test_default(self, click_runner, mocker, mock_run):
        mock_apply_release = mocker.patch(
            "build_harness.commands.wheel._apply_release_id"
        )
        result = click_runner.invoke(
            main,
            [
                "package",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    ["/some/conftest/path/flit", "build"],
                ),
            ]
        )
        mock_apply_release.assert_not_called()

    def test_release_id_set(self, click_runner, mocker, mock_run):
        mock_apply_release = mocker.patch(
            "build_harness.commands.wheel._apply_release_id"
        )

        expected_id = "3.14.159"

        result = click_runner.invoke(
            main,
            [
                "package",
                "--release-id",
                expected_id,
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    ["/some/conftest/path/flit", "build"],
                ),
            ]
        )
        mock_apply_release.assert_called_once_with(expected_id, mocker.ANY)

    def test_empty_release_id(self, click_runner, mocker, mock_run):
        mock_apply_release = mocker.patch(
            "build_harness.commands.wheel._apply_release_id"
        )
        result = click_runner.invoke(
            main,
            [
                "package",
                "--release-id",
                "",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    ["/some/conftest/path/flit", "build"],
                ),
            ]
        )
        mock_apply_release.assert_not_called()
