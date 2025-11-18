#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Unit tests subcommand implementation."""

import logging
import pathlib
import sys
import typing

import click

from build_harness._utility import (
    extract_coverage,
    report_console_error,
    run_command,
)
from build_harness.project import acquire_source_dir
from build_harness.tools import CommandOptionsTestTool, PytestCommand

from .state import CommandState, ExitState

log = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = "dist"
DEFAULT_TEST_DIR = "tests"

COVERAGE_REPORT_ARGUMENTS = [
    "--coverage-console",
    "--coverage-html",
    "--coverage-xml",
]


class UnitTestError(Exception):
    """Problem occurred during running unit tests."""


class FailureTestToolError(UnitTestError):
    """At least one unit test failed."""


class CoverageTestToolError(UnitTestError):
    """Test coverage failed to meet or exceed the defined threshold."""


def _run_tests(
    command_options: CommandOptionsTestTool,
    coverage_threshold: typing.Optional[int],
    coverage_console: bool,
) -> None:
    """
    Run the unit tests.

    Args:
        command_options: pytest command options.
        coverage_threshold: If defined, the coverage threshold to test against.
        coverage_console: Enable coverage report to console.
    """
    this_pytest = PytestCommand(command_options)

    result = run_command(
        this_pytest.command(),
        capture_output=True,
    )
    if (result.returncode not in [0, 5]) or (
        (result.returncode == 5) and (not command_options["pass_zero_tests"])
    ):
        message = "unit tests failed. See log for details"
        log.debug(message)
        raise FailureTestToolError(message)
    elif result.returncode == 5:
        log.warning("Zero tests found, but options require exiting clean")

    if (coverage_threshold is not None) and result.stdout:
        report_text = result.stdout
        log.debug("coverage report, {0}".format(report_text))
        actual_coverage = extract_coverage(report_text)
        if actual_coverage < coverage_threshold:
            message = (
                "Coverage test failed, {0} (actual) < {1} (threshold)".format(
                    actual_coverage, coverage_threshold
                )
            )
            log.debug(message)
            raise CoverageTestToolError(message)
        else:
            click.echo("Total coverage, {0}".format(actual_coverage))
    elif (coverage_threshold is not None) and (not result.stdout):
        message = "no coverage report captured. See log for details"
        log.debug(message)
        raise CoverageTestToolError(message)

    if coverage_console and result.stdout:
        click.echo(result.stdout)


def _process_html_coverage(
    coverage_html: bool,
    coverage_html_dir: typing.Optional[str],
    output_path: pathlib.Path,
) -> typing.Tuple[bool, typing.Optional[pathlib.Path]]:
    html_coverage_path: typing.Optional[pathlib.Path]

    html_coverage_enabled = True
    if (not coverage_html_dir) and coverage_html:
        html_coverage_path = output_path / "coverage_report"
    elif coverage_html_dir:
        html_coverage_path = pathlib.Path(coverage_html_dir)
    else:
        html_coverage_enabled = False
        html_coverage_path = None

    log.debug("HTML coverage enabled, {0}".format(str(html_coverage_enabled)))
    log.debug("HTML coverage path, {0}".format(str(html_coverage_path)))

    return html_coverage_enabled, html_coverage_path


def _process_xml_coverage(
    coverage_xml: bool,
    coverage_xml_file: typing.Optional[str],
    output_path: pathlib.Path,
) -> typing.Tuple[bool, typing.Optional[pathlib.Path]]:
    xml_coverage_path: typing.Optional[pathlib.Path]

    xml_coverage_enabled = True
    if (not coverage_xml_file) and coverage_xml:
        xml_coverage_path = output_path / "coverage_report.xml"
    elif coverage_xml_file:
        xml_coverage_path = pathlib.Path(coverage_xml_file)
    else:
        xml_coverage_enabled = False
        xml_coverage_path = None

    log.debug("XML coverage enabled, {0}".format(str(xml_coverage_enabled)))
    log.debug("XML coverage path, {0}".format(str(xml_coverage_path)))

    return xml_coverage_enabled, xml_coverage_path


def _process_junitxml(
    junitxml: bool,
    junitxml_file: typing.Optional[str],
    output_path: pathlib.Path,
) -> typing.Tuple[bool, typing.Optional[pathlib.Path]]:
    junitxml_path: typing.Optional[pathlib.Path]

    junitxml_enabled = True
    if (not junitxml_file) and junitxml:
        junitxml_path = output_path / "junit_report.xml"
    elif junitxml_file:
        junitxml_path = pathlib.Path(junitxml_file)
    else:
        junitxml_enabled = False
        junitxml_path = None

    log.debug(
        "JUnit XML test report enabled, {0}".format(str(junitxml_enabled))
    )
    log.debug("JUnit XML test report path, {0}".format(str(junitxml_path)))

    return junitxml_enabled, junitxml_path


@click.command()
@click.pass_context
@click.option(
    "--check",
    "coverage_check",
    default=None,
    help="Test coverage against the specified threshold. [default: disabled]",
    type=int,
)
@click.option(
    COVERAGE_REPORT_ARGUMENTS[0],
    default=False,
    help="Enable console coverage report.",
    is_flag=True,
    show_default=True,
)
@click.option(
    COVERAGE_REPORT_ARGUMENTS[1],
    default=False,
    help="Enable HTML coverage report.",
    is_flag=True,
)
@click.option(
    "{0}-file".format(COVERAGE_REPORT_ARGUMENTS[1]),
    default="",
    help="Enable HTML coverage report. [default: auto directory location when "
    "enabled]",
    metavar="DIRECTORY",
    type=str,
)
@click.option(
    COVERAGE_REPORT_ARGUMENTS[2],
    default=False,
    help="Enable XML coverage report.",
    is_flag=True,
    type=str,
)
@click.option(
    "{0}-file".format(COVERAGE_REPORT_ARGUMENTS[2]),
    default="",
    help="Enable XML coverage report. [default: auto file location, when "
    "enabled]",
    metavar="FILE",
    show_default=True,
    type=str,
)
@click.option(
    "--junitxml",
    default=False,
    help="Enable junit XML test report.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "--junitxml-file",
    default=None,
    help="Path to junit XML test report. [default: disabled, default auto file "
    "location when enabled]",
    metavar="FILE",
    show_default=True,
    type=str,
)
@click.option(
    "--output-dir",
    default=DEFAULT_OUTPUT_DIR,
    help="Path to directory for placing output artifacts such as coverage "
    "report files.",
    metavar="DIRECTORY",
    show_default=True,
    type=str,
)
@click.option(
    "--pass-zero-tests",
    default=False,
    help="Pass (exit clean) when there are zero tests found.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "--source-dir",
    default="",
    help="Path to source directory. [default: acquire from project]",
    metavar="DIRECTORY",
    type=str,
)
@click.option(
    "--test-dir",
    default=DEFAULT_TEST_DIR,
    help="Path to unit test directory.",
    metavar="DIRECTORY",
    show_default=True,
    type=str,
)
def unit_test(
    ctx: click.Context,
    coverage_check: typing.Optional[int],
    coverage_console: bool,
    coverage_html: bool,
    coverage_html_file: typing.Optional[str],
    coverage_xml: bool,
    coverage_xml_file: typing.Optional[str],
    junitxml: bool,
    junitxml_file: typing.Optional[str],
    output_dir: str,
    pass_zero_tests: bool,
    source_dir: str,
    test_dir: str,
) -> None:
    """
    Run tests using the ``pytest`` unit test framework.

    When enabled, any reports will be automatically placed in the output
    artifact directory unless an alternative location is specified to the
    relevant argument.
    """
    try:
        ctx.ensure_object(dict)
        command_state: CommandState = ctx.obj["command_state"]

        output_path = pathlib.Path(output_dir)

        if not source_dir:
            source_dir = acquire_source_dir(pathlib.Path.cwd())

        html_coverage_enabled, html_coverage_path = _process_html_coverage(
            coverage_html, coverage_html_file, output_path
        )
        xml_coverage_enabled, xml_coverage_path = _process_xml_coverage(
            coverage_xml, coverage_xml_file, output_path
        )
        junitxml_enabled, junitxml_path = _process_junitxml(
            junitxml, junitxml_file, output_path
        )

        if coverage_check:
            coverage_console = True

        command_options: CommandOptionsTestTool = {
            "output_path": output_path,
            "source_path": pathlib.Path(source_dir),
            "test_path": pathlib.Path(test_dir),
            "venv_path": command_state.venv_path,
            "pass_zero_tests": pass_zero_tests,
            "report_enabled": {
                "html": html_coverage_enabled,
                "term-missing": coverage_console,
                "xml": xml_coverage_enabled,
                "junitxml": junitxml_enabled,
            },
            "report_dirs": {
                "html": html_coverage_path,
                "term-missing": None,
                "xml": xml_coverage_path,
                "junitxml": junitxml_path,
            },
        }

        _run_tests(command_options, coverage_check, coverage_console)
    except CoverageTestToolError:
        report_console_error("Test coverage has failed.")
        sys.exit(ExitState.TEST_COVERAGE_FAILED.value)
    except FailureTestToolError:
        report_console_error("Tests have failed.")
        sys.exit(ExitState.TESTS_FAILED.value)
    except Exception:
        message = "Unexpected error. Check log for details."
        log.exception(message)
        report_console_error(message)
        sys.exit(ExitState.UNKNOWN_ERROR.value)
