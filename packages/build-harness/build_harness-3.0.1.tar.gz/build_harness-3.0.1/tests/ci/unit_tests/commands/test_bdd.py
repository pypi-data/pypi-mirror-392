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
from build_harness.commands.bdd.run_tests import AcceptanceTestsError, _run_bdd
from tests.ci.support.click_runner import click_runner  # noqa: F401

MOCK_VENV_PATH = pathlib.Path("/some/test_bdd/path")
EXPECTED_BEHAVE_PATH = str(MOCK_VENV_PATH / "behave")


@pytest.fixture()
def clean_exists_tests(mocker):
    mocker.patch.object(pathlib.Path, "exists", return_value=False)
    mocker.patch.object(pathlib.Path, "mkdir")


@pytest.fixture()
def clean_dir_tests(mocker):
    mocker.patch.object(pathlib.Path, "exists", return_value=True)
    mocker.patch.object(pathlib.Path, "is_dir", return_value=True)


@pytest.fixture()
def not_dir_tests(mocker):
    mocker.patch.object(pathlib.Path, "exists", return_value=True)
    mocker.patch.object(pathlib.Path, "is_dir", return_value=False)


class TestRunBdd:
    def test_disabled(self, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            return_value=mock_result,
        )

        _run_bdd(MOCK_VENV_PATH, False, pathlib.Path("some/xml/path"), list())

        mock_run.assert_called_once_with(
            [
                EXPECTED_BEHAVE_PATH,
                "--format",
                "pretty",
                "--tags",
                "~@notimplemented",
                "--tags",
                "~@nottestable",
                "features",
            ]
        )

    def test_enabled_nonexistent_dir(self, clean_exists_tests, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            return_value=mock_result,
        )

        _run_bdd(MOCK_VENV_PATH, True, pathlib.Path("some/xml/path"), list())

        mock_run.assert_called_once_with(
            [
                EXPECTED_BEHAVE_PATH,
                "--format",
                "pretty",
                "--junit",
                "--junit-directory",
                "some/xml/path",
                "--tags",
                "~@notimplemented",
                "--tags",
                "~@nottestable",
                "features",
            ]
        )

    def test_enabled_existent_dir(self, clean_dir_tests, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            return_value=mock_result,
        )

        _run_bdd(MOCK_VENV_PATH, True, pathlib.Path("dist/behave"), list())

        mock_run.assert_called_once_with(
            [
                EXPECTED_BEHAVE_PATH,
                "--format",
                "pretty",
                "--junit",
                "--junit-directory",
                "dist/behave",
                "--tags",
                "~@notimplemented",
                "--tags",
                "~@nottestable",
                "features",
            ]
        )

    def test_tag_list(self, clean_dir_tests, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            return_value=mock_result,
        )

        _run_bdd(
            MOCK_VENV_PATH,
            True,
            pathlib.Path("dist/behave"),
            ["@some.tag", "@other.tag,@this.thing"],
        )

        mock_run.assert_called_once_with(
            [
                EXPECTED_BEHAVE_PATH,
                "--format",
                "pretty",
                "--junit",
                "--junit-directory",
                "dist/behave",
                "--tags",
                "~@notimplemented",
                "--tags",
                "~@nottestable",
                "--tags",
                "@some.tag",
                "--tags",
                "@other.tag,@this.thing",
                "features",
            ]
        )

    def test_enabled_non_dir(self, not_dir_tests):
        with pytest.raises(
            AcceptanceTestsError,
            match=r"^JUnit XML location must be a " r"directory",
        ):
            _run_bdd(MOCK_VENV_PATH, True, pathlib.Path("dist/behave"), list())


class TestAcceptanceTests:
    def test_default(self, clean_exists_tests, click_runner, mocker):
        mock_behave_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_behave_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            side_effect=[mock_behave_result],
        )
        build_harness.commands.build_harness_group.sys.argv = [
            str(MOCK_VENV_PATH / "build-harness")
        ]
        result = click_runner.invoke(main, ["acceptance", "tests"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        EXPECTED_BEHAVE_PATH,
                        "--format",
                        "pretty",
                        "--tags",
                        "~@notimplemented",
                        "--tags",
                        "~@nottestable",
                        "features",
                    ]
                ),
            ]
        )

    def test_unknown_error(self, clean_exists_tests, click_runner, mocker):
        mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            side_effect=RuntimeError(),
        )
        result = click_runner.invoke(main, ["acceptance", "tests"])

        assert result.exit_code == ExitState.UNKNOWN_ERROR.value

    def test_junit_enabled(self, click_runner, mocker):
        mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_isort_result.returncode = 0
        mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_black_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            side_effect=[mock_isort_result, mock_black_result],
        )
        build_harness.commands.build_harness_group.sys.argv = [
            str(MOCK_VENV_PATH / "build-harness")
        ]
        result = click_runner.invoke(
            main, ["acceptance", "tests", "--junitxml"]
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        EXPECTED_BEHAVE_PATH,
                        "--format",
                        "pretty",
                        "--junit",
                        "--junit-directory",
                        "dist/behave",
                        "--tags",
                        "~@notimplemented",
                        "--tags",
                        "~@nottestable",
                        "features",
                    ]
                ),
            ]
        )

    def test_junit_alternate_dir(self, click_runner, mocker):
        expected_dir = "some/test_bdd/junit/dir"

        mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_isort_result.returncode = 0
        mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_black_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            side_effect=[mock_isort_result, mock_black_result],
        )
        mocker.patch("build_harness.commands.bdd.run_tests._check_junit_dir")
        build_harness.commands.build_harness_group.sys.argv = [
            str(MOCK_VENV_PATH / "build-harness")
        ]
        result = click_runner.invoke(
            main,
            [
                "acceptance",
                "tests",
                "--junitxml",
                "--junitxml-dir",
                expected_dir,
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        EXPECTED_BEHAVE_PATH,
                        "--format",
                        "pretty",
                        "--junit",
                        "--junit-directory",
                        expected_dir,
                        "--tags",
                        "~@notimplemented",
                        "--tags",
                        "~@nottestable",
                        "features",
                    ]
                ),
            ]
        )

    def test_tag_list(self, click_runner, mocker):
        mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_isort_result.returncode = 0
        mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_black_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.run_tests.run_command",
            side_effect=[mock_isort_result, mock_black_result],
        )
        build_harness.commands.build_harness_group.sys.argv = [
            "/some/test_bdd/path/build-harness"
        ]
        result = click_runner.invoke(
            main,
            [
                "acceptance",
                "tests",
                "--tags",
                "@some.tag",
                "--tags",
                "@other.tag,@this.thing",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        EXPECTED_BEHAVE_PATH,
                        "--format",
                        "pretty",
                        "--tags",
                        "~@notimplemented",
                        "--tags",
                        "~@nottestable",
                        "--tags",
                        "@some.tag",
                        "--tags",
                        "@other.tag,@this.thing",
                        "features",
                    ]
                ),
            ]
        )


class TestSnippets:
    def test_clean(self, click_runner, mocker):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.snippets.run_command",
            side_effect=[mock_result],
        )
        build_harness.commands.build_harness_group.sys.argv = [
            str(MOCK_VENV_PATH / "build-harness")
        ]
        result = click_runner.invoke(main, ["acceptance", "snippets"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        EXPECTED_BEHAVE_PATH,
                        "--snippets",
                        "--tags",
                        "@notimplemented",
                        "features",
                    ]
                ),
            ]
        )


class TestTags:
    def test_clean(self, click_runner, mocker):
        mock_isort_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_isort_result.returncode = 0
        mock_black_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_black_result.returncode = 0
        mock_run = mocker.patch(
            "build_harness.commands.bdd.tags.run_command",
            side_effect=[mock_isort_result, mock_black_result],
        )
        build_harness.commands.build_harness_group.sys.argv = [
            str(MOCK_VENV_PATH / "build-harness")
        ]
        result = click_runner.invoke(main, ["acceptance", "tags"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        EXPECTED_BEHAVE_PATH,
                        "--format",
                        "tags.location",
                        "features",
                    ]
                ),
            ]
        )
