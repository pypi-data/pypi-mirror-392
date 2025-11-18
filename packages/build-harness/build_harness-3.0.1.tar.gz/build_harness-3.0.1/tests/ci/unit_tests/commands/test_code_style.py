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

import pytest

import build_harness.commands.build_harness_group
from build_harness.commands import ExitState, main
from build_harness.commands.code_style import (
    BlackCheckError,
    FormattingError,
    IsortCheckError,
    _apply_formatting,
    _check_formatting,
)
from tests.ci.support.click_runner import click_runner  # noqa: F401

MOCK_VENV_PATH = pathlib.Path("/some/test_code_style/path")


class TestApplyFormatting:
    def test_clean(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            return_value=mock_result,
        )

        _apply_formatting(MOCK_VENV_PATH)

    def test_black_error(self, mocker):
        mock_results = [mocker.MagicMock(), mocker.MagicMock()]
        mock_results[0].returncode = 0
        mock_results[1].returncode = 1
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=mock_results,
        )

        with pytest.raises(
            FormattingError,
            match=r"^isort and/or black failed during formatting.",
        ):
            _apply_formatting(MOCK_VENV_PATH)

    def test_isort_error(self, mocker):
        mock_results = [mocker.MagicMock(), mocker.MagicMock()]
        mock_results[0].returncode = 1
        mock_results[1].returncode = 0
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=mock_results,
        )

        with pytest.raises(
            FormattingError,
            match=r"^isort and/or black failed during formatting.",
        ):
            _apply_formatting(MOCK_VENV_PATH)


class TestCheckFormatting:
    def test_clean(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            return_value=mock_result,
        )

        _check_formatting(MOCK_VENV_PATH)

    def test_black_failure(self, mocker):
        mock_results = [mocker.MagicMock(), mocker.MagicMock()]
        mock_results[0].returncode = 0
        mock_results[1].returncode = 1
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=mock_results,
        )

        with pytest.raises(BlackCheckError, match=r"^black check failed"):
            _check_formatting(MOCK_VENV_PATH)

    def test_isort_failure(self, mocker):
        mock_results = [mocker.MagicMock(), mocker.MagicMock()]
        mock_results[0].returncode = 1
        mock_results[1].returncode = 0
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=mock_results,
        )

        with pytest.raises(IsortCheckError, match=r"^isort check failed"):
            _check_formatting(MOCK_VENV_PATH)


class TestFormatting:
    def test_clean(self, click_runner, mocker):
        mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_isort_result.returncode = 0
        mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_black_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=[mock_isort_result, mock_black_result],
        )
        build_harness.commands.build_harness_group.sys.argv = [
            "/some/test_code_style_formatting_clean/path/build-harness"
        ]
        result = click_runner.invoke(main, ["formatting"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/test_code_style_formatting_clean/path/isort",
                        "--profile",
                        "black",
                        ".",
                    ]
                ),
                mocker.call(
                    ["/some/test_code_style_formatting_clean/path/black", "."]
                ),
            ]
        )

    def test_unknown_error(self, click_runner, mocker):
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=RuntimeError(),
        )
        result = click_runner.invoke(main, ["formatting"])

        assert result.exit_code == ExitState.UNKNOWN_ERROR.value


class TestCheckArgument:
    def test_isort_fails(self, click_runner, mocker):
        mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_isort_result.returncode = 1
        mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_black_result.returncode = 0
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=[mock_isort_result, mock_black_result],
        )
        result = click_runner.invoke(main, ["formatting", "--check"])

        assert result.exit_code == ExitState.ISORT_CHECK_FAILED.value

    def test_black_fails(self, click_runner, mocker):
        mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_isort_result.returncode = 0
        mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_black_result.returncode = 1
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=[mock_isort_result, mock_black_result],
        )
        result = click_runner.invoke(main, ["formatting", "--check"])

        assert result.exit_code == ExitState.BLACK_CHECK_FAILED.value

    def test_check_passes(self, click_runner, mocker):
        mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_isort_result.returncode = 0
        mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_black_result.returncode = 0
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=[mock_isort_result, mock_black_result],
        )
        result = click_runner.invoke(main, ["formatting", "--check"])

        assert result.exit_code == 0

    def test_check_unknown_error(self, click_runner, mocker):
        mocker.patch(
            "build_harness.commands.code_style.run_command",
            side_effect=RuntimeError(),
        )
        result = click_runner.invoke(main, ["formatting", "--check"])

        assert result.exit_code == ExitState.UNKNOWN_ERROR.value
