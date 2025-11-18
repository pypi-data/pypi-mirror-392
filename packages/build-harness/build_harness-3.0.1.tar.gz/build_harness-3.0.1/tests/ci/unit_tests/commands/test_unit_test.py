#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import copy
import pathlib
import subprocess

import pytest

from build_harness.commands import main
from build_harness.commands.unit_tests import (
    CommandOptionsTestTool,
    CoverageTestToolError,
    ExitState,
    UnitTestError,
    _run_tests,
)
from tests.ci.support.click_runner import click_runner  # noqa: F401

MOCK_VENV_PATH = pathlib.Path("/some/test_unit_test/path")


class TestRunTests:
    MOCK_OPTIONS: CommandOptionsTestTool = {
        "output_path": pathlib.Path("dist/path"),
        "source_path": pathlib.Path("source/path"),
        "test_path": pathlib.Path("test/path"),
        "venv_path": pathlib.Path("venv/path"),
        "pass_zero_tests": False,
        "report_enabled": {
            "junitxml": False,
            "term-missing": True,
            "html": False,
            "xml": False,
        },
        "report_dirs": {
            "junitxml": None,
            "term-missing": None,
            "html": None,
            "xml": None,
        },
    }

    def test_clean(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        _run_tests(self.MOCK_OPTIONS, None, False)

    def test_failed_raises(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.returncode = 1
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        with pytest.raises(UnitTestError, match=r"^unit tests failed"):
            _run_tests(self.MOCK_OPTIONS, None, False)

    def test_above_threshold(self, mocker):
        mock_captured_report = """some/file.py                     5      0   100%
--------------------------------------------------------
TOTAL                                  170     44    91%
"""
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_captured_report
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        _run_tests(self.MOCK_OPTIONS, 90, False)

    def test_equal_threshold(self, mocker):
        mock_captured_report = """some/file.py                     5      0   100%
--------------------------------------------------------
TOTAL                                  170     44    90%
"""
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_captured_report
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        _run_tests(self.MOCK_OPTIONS, 90, False)

    def test_below_threshold(self, mocker):
        mock_captured_report = """some/file.py                     5      0   100%
--------------------------------------------------------
TOTAL                                  170     44    89%
"""
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_captured_report
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        with pytest.raises(
            CoverageTestToolError, match=r"^Coverage test failed"
        ):
            _run_tests(self.MOCK_OPTIONS, 90, False)

    def test_100_percent(self, mocker) -> None:
        mock_captured_report = """some/file.py                     5      0   100%
--------------------------------------------------------
TOTAL                                  170     44    100%
"""
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_captured_report
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        _run_tests(self.MOCK_OPTIONS, 90, False)

    def test_0_percent(self, mocker) -> None:
        mock_captured_report = """some/file.py                     5      0   100%
--------------------------------------------------------
TOTAL                                  170     44    0%
"""
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_captured_report
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        _run_tests(self.MOCK_OPTIONS, 0, False)

    def test_no_report_raises(self, mocker) -> None:
        mock_result = mocker.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = None
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        with pytest.raises(
            CoverageTestToolError, match=r"^no coverage report captured"
        ):
            _run_tests(self.MOCK_OPTIONS, 0, False)

    def test_no_tests_raises(self, mocker):
        """Zero tests raises an exception."""
        mock_options = copy.deepcopy(self.MOCK_OPTIONS)
        mock_options["pass_zero_tests"] = False

        mock_result = mocker.MagicMock()
        mock_result.returncode = 5
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        with pytest.raises(UnitTestError, match=r"^unit tests failed"):
            _run_tests(mock_options, None, False)

    def test_no_tests_fail_disabled(self, mocker):
        """Disabling failure for no tests does not raise."""
        mock_options = copy.deepcopy(self.MOCK_OPTIONS)
        mock_options["pass_zero_tests"] = True

        mock_result = mocker.MagicMock()
        mock_result.returncode = 5
        mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )

        _run_tests(mock_options, None, False)


class TestUnitTest:
    def test_pass(self, click_runner, mocker, mock_sysargv):
        mock_pytest_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_pytest_result.returncode = 0
        mock_pytest_result.stdout = b""
        mock_run = mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            side_effect=[mock_pytest_result],
        )
        mocker.patch(
            "build_harness.commands.unit_tests.acquire_source_dir",
            return_value="the/source/path",
        )
        result = click_runner.invoke(main, ["unit-test"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=the/source/path",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_fail(self, click_runner, mocker, mock_sysargv):
        mock_pytest_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_pytest_result.returncode = 1
        mock_pytest_result.stdout = b""
        mock_run = mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            side_effect=[mock_pytest_result],
        )
        mocker.patch(
            "build_harness.commands.unit_tests.acquire_source_dir",
            return_value="the/source/path",
        )
        result = click_runner.invoke(main, ["unit-test"])

        assert result.exit_code == ExitState.TESTS_FAILED.value
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=the/source/path",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )


@pytest.fixture()
def mock_sourcedir(mocker):
    mocker.patch(
        "build_harness.commands.unit_tests.acquire_source_dir",
        return_value="source/path",
    )


@pytest.fixture()
def mock_run(mock_sysargv, mock_sourcedir, mocker):
    mock_pytest_result = mocker.create_autospec(subprocess.CompletedProcess)
    mock_pytest_result.returncode = 0
    mock_pytest_result.stdout = b""
    this_run = mocker.patch(
        "build_harness.commands.unit_tests.run_command",
        side_effect=[mock_pytest_result],
    )

    return this_run


class TestCoverageReports:
    def test_coverage_console(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(
            main,
            [
                "unit-test",
                "--coverage-console",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--cov-report",
                        "term-missing",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_coverage_html_auto(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(main, ["unit-test", "--coverage-html"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--cov-report",
                        "html:dist/coverage_report",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_coverage_html_explicit(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(
            main,
            [
                "unit-test",
                "--coverage-html",
                "--coverage-html-file",
                "some/html/path",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--cov-report",
                        "html:some/html/path",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_coverage_xml_auto(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(main, ["unit-test", "--coverage-xml"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_coverage_xml_explicit(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(
            main,
            [
                "unit-test",
                "--coverage-xml",
                "--coverage-xml-file",
                "some/xml/file",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--cov-report",
                        "xml:some/xml/file",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_multiple_coverage(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(
            main,
            [
                "unit-test",
                "--coverage-console",
                "--coverage-html",
                "--coverage-xml",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--cov-report",
                        "html:dist/coverage_report",
                        "--cov-report",
                        "term-missing",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )


class TestJunitReport:
    def test_junitxml_auto(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(main, ["unit-test", "--junitxml"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--junitxml=dist/junit_report.xml",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_junitxml_explicit(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(
            main, ["unit-test", "--junitxml-file", "some/junit/file"]
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--junitxml=some/junit/file",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )


class TestCoverageCheck:
    mock_captured_report = """some/file.py                     5      0   100%
    --------------------------------------------------------
    TOTAL                                  170     44    91%
    """

    def test_pass(self, click_runner, mocker, mock_sysargv, mock_sourcedir):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = self.mock_captured_report
        mock_run = mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )
        result = click_runner.invoke(main, ["unit-test", "--check", "91"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--cov-report",
                        "term-missing",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_fail(self, click_runner, mocker, mock_sysargv, mock_sourcedir):
        mock_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = self.mock_captured_report
        mock_run = mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            return_value=mock_result,
        )
        result = click_runner.invoke(main, ["unit-test", "--check", "92"])

        assert result.exit_code == ExitState.TEST_COVERAGE_FAILED.value
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=source/path",
                        "--cov-report",
                        "term-missing",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )

    def test_pass_zero_tests(self, click_runner, mocker, mock_sysargv):
        mock_pytest_result = mocker.create_autospec(subprocess.CompletedProcess)
        mock_pytest_result.returncode = 5
        mock_pytest_result.stdout = ""
        mock_run = mocker.patch(
            "build_harness.commands.unit_tests.run_command",
            side_effect=[mock_pytest_result],
        )
        mocker.patch(
            "build_harness.commands.unit_tests.acquire_source_dir",
            return_value="the/source/path",
        )
        result = click_runner.invoke(main, ["unit-test", "--pass-zero-tests"])

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/pytest",
                        "--cov=the/source/path",
                        "--cov-report",
                        "xml:dist/coverage_report.xml",
                        "tests",
                    ],
                    capture_output=True,
                ),
            ]
        )
