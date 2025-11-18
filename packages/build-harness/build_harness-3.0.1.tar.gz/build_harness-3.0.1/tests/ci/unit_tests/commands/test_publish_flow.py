#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib
import tempfile

import pytest

from build_harness import __version__
from build_harness.commands._publish_flow import (
    GitNotFoundError,
    PublishOptions,
    publish_flow_main,
)
from build_harness.commands.state import ExitState
from build_harness.tools.git import TagData
from tests.ci.support.click_runner import click_runner  # noqa: F401


class TestPublishFlowProject:
    def test_project(self, click_runner, mocker):
        expected_repo_path = "some/path"
        mock_get_tag = mocker.patch(
            "build_harness.commands._publish_flow.get_tag_data",
            return_value=TagData(tag="3.14.159", offset=11),
        )

        result = click_runner.invoke(
            publish_flow_main, ["--project", expected_repo_path]
        )

        assert result.exit_code == 0
        mock_get_tag.assert_called_once_with(
            pathlib.Path(expected_repo_path), mocker.ANY
        )
        assert result.output == PublishOptions.test.name

    def test_bad_repo(self, click_runner):
        with tempfile.TemporaryDirectory() as this_dir:
            result = click_runner.invoke(
                publish_flow_main, ["--project", this_dir]
            )

            assert result.exit_code == ExitState.BAD_REPO.value
            assert "FAILED: Invalid git repository" in result.output

    def test_bad_git(self, click_runner, mocker):
        mocker.patch(
            "build_harness.commands._publish_flow.validate_git",
            side_effect=GitNotFoundError(
                "Git must be installed to use this utility"
            ),
        )
        result = click_runner.invoke(publish_flow_main, ["--git", "bad/path"])

        assert result.exit_code == ExitState.BAD_GIT_EXE.value
        assert (
            "Git must be installed and configured to use this utility"
            in result.output
        )
        assert (
            "sudo apt install -y git || sudo yum install git" in result.output
        )


class TestPublishFlowDefaultBranch:
    def test_default_branch(self, click_runner, mocker):
        expected_branch = "alternate_main"
        mock_get_tag = mocker.patch(
            "build_harness.commands._publish_flow.get_tag_data",
            return_value=TagData(tag="3.14.159"),
        )

        result = click_runner.invoke(
            publish_flow_main, ["--default-branch", expected_branch]
        )

        assert result.exit_code == 0
        mock_get_tag.assert_called_once_with(mocker.ANY, expected_branch)


class TestPublishFlowStockOptions:
    def test_help(self, click_runner):
        result = click_runner.invoke(publish_flow_main, ["--help"])

        assert result.exit_code == 0
        assert "Usage: publish-flow-main" in result.output

    def test_version(self, click_runner):
        result = click_runner.invoke(publish_flow_main, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.output


class TestPublishFlowActivation:
    def test_semver_release(self, click_runner, mocker):
        data = [
            {"arguments": [], "result": PublishOptions.yes.name},
            {
                "arguments": ["--publish-prerelease"],
                "result": PublishOptions.yes.name,
            },
            {
                "arguments": ["--publish-nonrelease"],
                "result": PublishOptions.yes.name,
            },
        ]
        mocker.patch(
            "build_harness.commands._publish_flow.get_tag_data",
            return_value=TagData(tag="3.14.159", offset=None),
        )

        _do_publish_result_test(data, click_runner)

    def test_semver_prerelease(self, click_runner, mocker):
        data = [
            {"arguments": [], "result": PublishOptions.test.name},
            {
                "arguments": ["--publish-prerelease"],
                "result": PublishOptions.yes.name,
            },
            {
                "arguments": ["--publish-nonrelease"],
                "result": PublishOptions.yes.name,
            },
        ]
        mocker.patch(
            "build_harness.commands._publish_flow.get_tag_data",
            return_value=TagData(
                tag="3.14.159-alpha.3",
                offset=None,
            ),
        )

        _do_publish_result_test(data, click_runner)

    def test_dryrun_tag(self, click_runner, mocker):
        """Dryun should result in "protected" job execution, so should never publish."""
        # and in case it does, pypi.org rejects the PEP-440 local suffix for upload.
        data = [
            {"arguments": [], "result": PublishOptions.dryrun.name},
            {
                "arguments": ["--publish-prerelease"],
                "result": PublishOptions.dryrun.name,
            },
            {
                "arguments": ["--publish-nonrelease"],
                "result": PublishOptions.dryrun.name,
            },
        ]
        mocker.patch(
            "build_harness.commands._publish_flow.get_tag_data",
            return_value=TagData(
                tag="3.14.159+dryrun",
                offset=None,
            ),
        )

        _do_publish_result_test(data, click_runner)

    def test_nonrelease(self, click_runner, mocker):
        data = [
            {"arguments": [], "result": PublishOptions.test.name},
            {
                "arguments": ["--publish-prerelease"],
                "result": PublishOptions.test.name,
            },
            {
                "arguments": ["--publish-nonrelease"],
                "result": PublishOptions.yes.name,
            },
        ]
        mocker.patch(
            "build_harness.commands._publish_flow.get_tag_data",
            return_value=TagData(tag="3.14.159", offset="1"),
        )

        _do_publish_result_test(data, click_runner)


def _do_publish_result_test(data: list, this_runner):
    for this_data in data:
        result = this_runner.invoke(publish_flow_main, this_data["arguments"])

        if result.exit_code != 0:
            pytest.fail(
                "Non-zero exit, {0}".format(str(this_data["arguments"]))
            )
        if result.output != this_data["result"]:
            pytest.fail(
                "Unexpected output, {0}, {1}, {2}".format(
                    str(this_data["arguments"]),
                    result.output,
                    this_data["result"],
                )
            )


class TestPublishFlowDisablePullRequestPublish:
    def test_nonrelease(self, click_runner, mocker):
        data = [
            {"arguments": [], "result": PublishOptions.test.name},
            {
                "arguments": ["--disable-pr-publish", "merge_request_event"],
                "result": PublishOptions.dryrun.name,
            },
            {
                "arguments": ["--disable-pr-publish", "anyothervalue"],
                "result": PublishOptions.test.name,
            },
        ]
        mocker.patch(
            "build_harness.commands._publish_flow.get_tag_data",
            return_value=TagData(tag="3.14.159", offset="10"),
        )

        _do_publish_result_test(data, click_runner)
