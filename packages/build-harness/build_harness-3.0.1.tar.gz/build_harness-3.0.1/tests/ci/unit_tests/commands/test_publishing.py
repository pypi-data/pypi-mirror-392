#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import logging
import pathlib
import subprocess
import tempfile

import pytest

from build_harness.commands import main
from build_harness.commands.publishing import PublishOptions, _publish_packages
from tests.ci.support.click_runner import click_runner  # noqa: F401


@pytest.fixture()
def mock_run(mock_sysargv, mocker):
    mock_pytest_result = mocker.create_autospec(subprocess.CompletedProcess)
    mock_pytest_result.returncode = 0
    mock_pytest_result.stdout = ""
    this_run = mocker.patch(
        "build_harness.commands.publishing.run_command",
        return_value=mock_pytest_result,
    )

    return this_run


class TestPublishPackages:
    MOCK_VENV = pathlib.Path("some/path")

    def test_yes(self, caplog, mock_run, mocker):
        with caplog.at_level(logging.DEBUG):
            _publish_packages(self.MOCK_VENV, PublishOptions.yes, None, None)

            mock_run.assert_has_calls(
                [
                    mocker.call(
                        mocker.ANY,
                        env=dict(),
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    )
                ]
            )
            assert "twine command run," in caplog.text

    def test_no(self, caplog, mock_run):
        with caplog.at_level(logging.DEBUG):
            _publish_packages(self.MOCK_VENV, PublishOptions.no, None, None)

            mock_run.assert_not_called()
            assert "Publish disabled" in caplog.text

    def test_dryrun(self, caplog, mock_run, mocker):
        with caplog.at_level(logging.DEBUG):
            _publish_packages(self.MOCK_VENV, PublishOptions.dryrun, None, None)

            mock_run.assert_has_calls(
                [
                    mocker.call(
                        mocker.ANY,
                        env={},
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    )
                ]
            )
            assert "Dry run," in caplog.text

    def test_test(self, caplog, mock_run, mocker):
        with caplog.at_level(logging.DEBUG):
            _publish_packages(self.MOCK_VENV, PublishOptions.test, None, None)

            mock_run.assert_has_calls(
                [
                    mocker.call(
                        mocker.ANY,
                        env=dict(),
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    )
                ]
            )
            assert "twine command run," in caplog.text

    def test_none_user_password(self, caplog, mock_run, mocker):
        with caplog.at_level(logging.DEBUG):
            _publish_packages(self.MOCK_VENV, PublishOptions.yes, None, None)

            mock_run.assert_has_calls(
                [
                    mocker.call(
                        mocker.ANY,
                        env=dict(),
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    )
                ]
            )

            assert "twine username not provided" in caplog.text
            assert "twine password not provided" in caplog.text

    def test_user(self, caplog, mock_run, mocker):
        with caplog.at_level(logging.DEBUG):
            _publish_packages(
                self.MOCK_VENV, PublishOptions.yes, None, "this_user"
            )

            mock_run.assert_has_calls(
                [
                    mocker.call(
                        mocker.ANY,
                        env={
                            "TWINE_USERNAME": "this_user",
                        },
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    )
                ]
            )
            assert "twine username," in caplog.text
            assert "twine password," not in caplog.text

    def test_password(self, caplog, mock_run, mocker):
        with caplog.at_level(logging.DEBUG):
            _publish_packages(
                self.MOCK_VENV, PublishOptions.yes, "this_password", None
            )

            mock_run.assert_has_calls(
                [
                    mocker.call(
                        mocker.ANY,
                        env={
                            "TWINE_PASSWORD": "this_password",
                        },
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    )
                ]
            )
            assert "twine username," not in caplog.text
            assert "twine password," in caplog.text

    def test_user_password(self, caplog, mock_run, mocker):
        with caplog.at_level(logging.DEBUG):
            _publish_packages(
                self.MOCK_VENV, PublishOptions.yes, "this_password", "this_user"
            )

            mock_run.assert_has_calls(
                [
                    mocker.call(
                        mocker.ANY,
                        env={
                            "TWINE_USERNAME": "this_user",
                            "TWINE_PASSWORD": "this_password",
                        },
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    )
                ]
            )
            assert "twine username," in caplog.text
            assert "twine password," in caplog.text


class ArrayContaining:
    """Matches if the array contains specified items"""

    def __init__(self, *expected_items):
        self.expected_items = expected_items

    def __eq__(self, other):
        if not isinstance(other, (list, tuple)):
            return False
        return all(item in other for item in self.expected_items)

    def __repr__(self):
        return f"ArrayContaining({self.expected_items})"


class TestPublish:
    def test_default(self, caplog, click_runner, mocker, mock_run):
        with caplog.at_level(logging.DEBUG):
            result = click_runner.invoke(
                main,
                [
                    "--log-console-enable",
                    "--log-level",
                    "debug",
                    "publish",
                    "--user",
                    "username",
                    "--password",
                    "password",
                ],
            )

            assert result.exit_code == 0
            mock_run.assert_has_calls(
                [
                    mocker.call(
                        [
                            "/some/conftest/path/twine",
                            "upload",
                            "--non-interactive",
                            "dist/*.whl",
                            "dist/*.tar.gz",
                        ],
                        env={
                            "TWINE_USERNAME": "username",
                            "TWINE_PASSWORD": "password",
                        },
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    ),
                ]
            )

            assert "twine command run," in caplog.text
            assert "twine username," in caplog.text
            assert "twine password," in caplog.text
            assert "password passed as CLI argument," in caplog.text
            # check that run_command logging is suppressed to protect credentials
            assert "command to run," not in caplog.text
            assert "command arguments," not in caplog.text

    def test_publish(self, click_runner, mocker, mock_run):
        result = click_runner.invoke(
            main,
            [
                "publish",
                "--user",
                "username",
                "--password",
                "password",
                "--publish",
                "yes",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    [
                        "/some/conftest/path/twine",
                        "upload",
                        "--non-interactive",
                        "dist/*.whl",
                        "dist/*.tar.gz",
                    ],
                    env={
                        "TWINE_PASSWORD": "password",
                        "TWINE_USERNAME": "username",
                    },
                    suppress_command_logging=True,
                    suppress_argument_logging=True,
                ),
            ]
        )

    def test_nopublish(self, click_runner, mock_run):
        result = click_runner.invoke(
            main,
            [
                "publish",
                "--user",
                "username",
                "--password",
                "password",
                "--publish",
                "no",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_not_called()

    def test_publish_dryrun(self, click_runner, mock_run, mocker):
        """dryrun overrides publish"""
        result = click_runner.invoke(
            main,
            [
                "publish",
                "--user",
                "username",
                "--password",
                "password",
                "--publish",
                "dryrun",
            ],
        )

        assert result.exit_code == 0
        mock_run.assert_has_calls(
            [
                mocker.call(
                    ArrayContaining("/some/conftest/path/twine", "check"),
                    env={
                        "TWINE_USERNAME": "username",
                        "TWINE_PASSWORD": "password",
                    },
                    suppress_command_logging=True,
                    suppress_argument_logging=True,
                )
            ]
        )

    def test_password_file(self, caplog, click_runner, mock_run, mocker):
        with caplog.at_level(
            logging.DEBUG
        ), tempfile.TemporaryDirectory() as dir:
            this_dir = pathlib.Path(dir)
            this_file = this_dir / "this-file"
            with this_file.open(mode="w") as f:
                f.write("this-password")

            result = click_runner.invoke(
                main,
                [
                    "--log-console-enable",
                    "--log-level",
                    "debug",
                    "publish",
                    "--user",
                    "username",
                    "--password-file",
                    str(this_file),
                ],
            )

            assert result.exit_code == 0

            mock_run.assert_has_calls(
                [
                    mocker.call(
                        mocker.ANY,
                        env={
                            "TWINE_USERNAME": "username",
                            "TWINE_PASSWORD": "this-password",
                        },
                        suppress_command_logging=True,
                        suppress_argument_logging=True,
                    )
                ]
            )
            assert "password specified in password file," in caplog.text
            assert "password recovered from file," in caplog.text
