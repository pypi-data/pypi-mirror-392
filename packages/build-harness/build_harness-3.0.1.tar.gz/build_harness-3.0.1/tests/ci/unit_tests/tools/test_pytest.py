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

from build_harness.tools import CommandOptionsTestTool, PytestCommand

MOCK_OPTIONS: CommandOptionsTestTool = {
    "output_path": pathlib.Path("dist"),
    "source_path": pathlib.Path("."),
    "test_path": pathlib.Path("tests"),
    "venv_path": pathlib.Path("some/venv/path"),
    "report_enabled": {
        "junitxml": False,
        "term-missing": False,
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


def test_default():
    this_options = copy.deepcopy(MOCK_OPTIONS)
    under_test = PytestCommand(this_options)

    assert under_test.command() == [
        "some/venv/path/pytest",
        "tests",
    ]


def test_source_dir():
    this_options = copy.deepcopy(MOCK_OPTIONS)
    this_options["source_path"] = pathlib.Path("some/source/path")
    under_test = PytestCommand(this_options)

    assert under_test.command() == [
        "some/venv/path/pytest",
        "tests",
    ]


def test_test_dir():
    this_options = copy.deepcopy(MOCK_OPTIONS)
    this_options["test_path"] = pathlib.Path("some/test/path")
    under_test = PytestCommand(this_options)

    assert under_test.command() == [
        "some/venv/path/pytest",
        "some/test/path",
    ]


def test_cov_term():
    this_options = copy.deepcopy(MOCK_OPTIONS)
    this_options["report_enabled"]["term-missing"] = True
    under_test = PytestCommand(this_options)

    assert under_test.command() == [
        "some/venv/path/pytest",
        "--cov=.",
        "--cov-report",
        "term-missing",
        "tests",
    ]


def test_cov_html_file():
    this_options = copy.deepcopy(MOCK_OPTIONS)
    this_options["report_enabled"]["html"] = True
    this_options["report_dirs"]["html"] = pathlib.Path("some/html/path")
    under_test = PytestCommand(this_options)

    assert under_test.command() == [
        "some/venv/path/pytest",
        "--cov=.",
        "--cov-report",
        "html:some/html/path",
        "tests",
    ]


def test_cov_xml_file():
    this_options = copy.deepcopy(MOCK_OPTIONS)
    this_options["report_enabled"]["xml"] = True
    this_options["report_dirs"]["xml"] = pathlib.Path("some/xml/path")
    under_test = PytestCommand(this_options)

    assert under_test.command() == [
        "some/venv/path/pytest",
        "--cov=.",
        "--cov-report",
        "xml:some/xml/path",
        "tests",
    ]


def test_junit_xml_file():
    this_options = copy.deepcopy(MOCK_OPTIONS)
    this_options["report_enabled"]["junitxml"] = True
    this_options["report_dirs"]["junitxml"] = pathlib.Path("some/junit/path")
    under_test = PytestCommand(this_options)

    assert under_test.command() == [
        "some/venv/path/pytest",
        "--cov=.",
        "--junitxml=some/junit/path",
        "tests",
    ]


def test_multiple_reports():
    this_options = copy.deepcopy(MOCK_OPTIONS)
    this_options["report_enabled"]["xml"] = True
    this_options["report_enabled"]["html"] = True
    under_test = PytestCommand(this_options)

    assert under_test.command() == [
        "some/venv/path/pytest",
        "--cov=.",
        "--cov-report",
        "html",
        "--cov-report",
        "xml",
        "tests",
    ]
