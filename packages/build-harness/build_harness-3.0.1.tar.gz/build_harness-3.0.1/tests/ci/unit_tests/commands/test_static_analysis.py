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

from build_harness.commands import ExitState, main
from build_harness.commands.analysis import (
    StaticAnalysisError,
    _apply_analysis,
    _run_flake8,
    _run_mypy,
)
from tests.ci.support.click_runner import click_runner  # noqa: F401

MOCK_PROJECT_PATH = pathlib.Path("project/path")
MOCK_VENV_PATH = pathlib.Path("/some/test_static_analysis/path")


class TestRunAnalyses:
    def test_flake8_dirty_exit_raises(self, mocker):
        mock_exit = mocker.MagicMock()
        mock_exit.returncode = 1
        mocker.patch(
            "build_harness.commands.analysis.run_command",
            return_value=mock_exit,
        )

        with pytest.raises(
            StaticAnalysisError, match=r"^flake8 analysis failed"
        ):
            _run_flake8(MOCK_PROJECT_PATH, MOCK_VENV_PATH)

    def test_mypy_dirty_exit_raises(self, mocker):
        mock_exit = mocker.MagicMock()
        mock_exit.returncode = 1
        mocker.patch(
            "build_harness.commands.analysis.run_command",
            return_value=mock_exit,
        )

        with pytest.raises(StaticAnalysisError, match=r"^mypy analysis failed"):
            _run_mypy(MOCK_PROJECT_PATH, MOCK_VENV_PATH)


class TestApplyAnalysis:
    def test_all_called(self, mocker):
        mock_flake8_run = mocker.patch(
            "build_harness.commands.analysis._run_flake8"
        )
        mock_mypy_run = mocker.patch(
            "build_harness.commands.analysis._run_mypy"
        )
        mocker.patch(
            "build_harness.commands.analysis.acquire_source_dir",
            return_value="this/source_dir",
        )

        _apply_analysis("all", MOCK_PROJECT_PATH, MOCK_VENV_PATH)

        mock_flake8_run.assert_called_once_with(
            MOCK_PROJECT_PATH / "this/source_dir", MOCK_VENV_PATH
        )
        mock_mypy_run.assert_called_once_with(
            MOCK_PROJECT_PATH / "this/source_dir", MOCK_VENV_PATH
        )

    def test_flake8_called(self, mocker):
        mock_flake8_run = mocker.patch(
            "build_harness.commands.analysis._run_flake8"
        )
        mocker.patch(
            "build_harness.commands.analysis.acquire_source_dir",
            return_value="this/source_dir",
        )

        _apply_analysis("flake8", MOCK_PROJECT_PATH, MOCK_VENV_PATH)

        mock_flake8_run.assert_called_once_with(
            MOCK_PROJECT_PATH / "this/source_dir", MOCK_VENV_PATH
        )

    def test_mypy_called(self, mocker):
        mock_mypy_run = mocker.patch(
            "build_harness.commands.analysis._run_mypy"
        )
        mocker.patch(
            "build_harness.commands.analysis.acquire_source_dir",
            return_value="this/source_dir",
        )

        _apply_analysis("mypy", MOCK_PROJECT_PATH, MOCK_VENV_PATH)

        mock_mypy_run.assert_called_once_with(
            MOCK_PROJECT_PATH / "this/source_dir", MOCK_VENV_PATH
        )


class TestStaticAnalysis:
    def test_unknown_error(self, click_runner, mocker):
        mocker.patch(
            "build_harness.commands.analysis._apply_analysis",
            side_effect=RuntimeError(),
        )
        result = click_runner.invoke(
            main, ["static-analysis", "--analysis", "flake8"]
        )

        assert result.exit_code == ExitState.UNKNOWN_ERROR.value


class TestAll:
    def test_default(self, click_runner, mocker):
        mock_analysis = mocker.patch(
            "build_harness.commands.analysis._apply_analysis"
        )
        mock_formatting = mocker.patch(
            "build_harness.commands.analysis._apply_formatting"
        )

        result = click_runner.invoke(main, ["static-analysis"])

        assert result.exit_code == 0
        mock_formatting.assert_called_once()
        mock_analysis.assert_called_once_with("all", mocker.ANY, mocker.ANY)

    def test_explicit(self, click_runner, mocker):
        mock_analysis = mocker.patch(
            "build_harness.commands.analysis._apply_analysis"
        )
        mock_formatting = mocker.patch(
            "build_harness.commands.analysis._apply_formatting"
        )

        result = click_runner.invoke(
            main, ["static-analysis", "--analysis", "all"]
        )

        assert result.exit_code == 0
        mock_formatting.assert_called_once()
        mock_analysis.assert_called_once_with("all", mocker.ANY, mocker.ANY)

    def test_flake8_failure(self, click_runner, mocker):
        mocker.patch("build_harness.commands.analysis._apply_formatting")
        mocker.patch(
            "build_harness.commands.analysis.acquire_source_dir",
            return_value="something",
        )
        mock_results = [mocker.create_autospec(subprocess.CompletedProcess)]
        mock_results[0].returncode = 1
        mocker.patch(
            "build_harness.commands.analysis.run_command",
            side_effect=mock_results,
        )

        result = click_runner.invoke(main, ["static-analysis"])

        assert result.exit_code == ExitState.FLAKE8_FAILED.value
        assert "flake8 analysis failed" in result.output

    def test_mypy_failure(self, click_runner, mocker):
        mocker.patch("build_harness.commands.analysis._apply_formatting")
        mocker.patch(
            "build_harness.commands.analysis.acquire_source_dir",
            return_value="something",
        )
        mock_results = [
            mocker.create_autospec(subprocess.CompletedProcess),
            mocker.create_autospec(subprocess.CompletedProcess),
        ]
        mock_results[0].returncode = 0
        mock_results[1].returncode = 1
        mocker.patch(
            "build_harness.commands.analysis.run_command",
            side_effect=mock_results,
        )

        result = click_runner.invoke(main, ["static-analysis"])

        assert result.exit_code == ExitState.MYPY_FAILED.value
        assert "mypy analysis failed" in result.output


class TestFlake8:
    def test_clean(self, click_runner, mocker):
        mock_analysis = mocker.patch(
            "build_harness.commands.analysis._apply_analysis"
        )
        mock_formatting = mocker.patch(
            "build_harness.commands.analysis._apply_formatting"
        )

        result = click_runner.invoke(
            main, ["static-analysis", "--analysis", "flake8"]
        )

        assert result.exit_code == 0
        mock_formatting.assert_called_once()
        mock_analysis.assert_called_once_with("flake8", mocker.ANY, mocker.ANY)

    def test_failure(self, click_runner, mocker):
        mocker.patch("build_harness.commands.analysis._apply_formatting")
        mocker.patch(
            "build_harness.commands.analysis.acquire_source_dir",
            return_value="something",
        )
        mock_results = [mocker.create_autospec(subprocess.CompletedProcess)]
        mock_results[0].returncode = 1
        mocker.patch(
            "build_harness.commands.analysis.run_command",
            side_effect=mock_results,
        )

        result = click_runner.invoke(
            main, ["static-analysis", "--analysis", "flake8"]
        )

        assert result.exit_code == ExitState.FLAKE8_FAILED.value
        assert "flake8 analysis failed" in result.output


class TestMypy:
    def test_clean(self, click_runner, mocker):
        mock_analysis = mocker.patch(
            "build_harness.commands.analysis._apply_analysis"
        )
        mock_formatting = mocker.patch(
            "build_harness.commands.analysis._apply_formatting"
        )

        result = click_runner.invoke(
            main, ["static-analysis", "--analysis", "mypy"]
        )

        assert result.exit_code == 0
        mock_formatting.assert_called_once()
        mock_analysis.assert_called_once_with("mypy", mocker.ANY, mocker.ANY)

    def test_failure(self, click_runner, mocker):
        mocker.patch("build_harness.commands.analysis._apply_formatting")
        mocker.patch(
            "build_harness.commands.analysis.acquire_source_dir",
            return_value="something",
        )
        mock_results = [mocker.create_autospec(subprocess.CompletedProcess)]
        mock_results[0].returncode = 1
        mocker.patch(
            "build_harness.commands.analysis.run_command",
            side_effect=mock_results,
        )

        result = click_runner.invoke(
            main, ["static-analysis", "--analysis", "mypy"]
        )

        assert result.exit_code == ExitState.MYPY_FAILED.value
        assert "mypy analysis failed" in result.output
