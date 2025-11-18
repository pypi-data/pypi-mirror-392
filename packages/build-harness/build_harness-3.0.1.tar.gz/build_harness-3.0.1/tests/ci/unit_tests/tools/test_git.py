#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import contextlib
import logging
import pathlib
import tempfile
import typing

import git
import pytest

from build_harness.tools.git import (
    GitError,
    GitNotFoundError,
    GitRepoError,
    TagData,
    TagDataError,
    _is_commit_tagged,
    _parse_describe,
    _validate_git_version,
    get_tag_data,
    validate_git,
)
from tests.ci.support.repo import (
    FeatureDryrunTagOnHead,
    FeatureDryrunTags,
    NoTags,
    TagBase,
    TagOnDefaultHeadOnFeature,
    TagOnHead,
)


class TestValidateGitVersion:
    def test_clean(self, mocker):
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_result.stdout = "git version 2.32.1 (Apple Git-133)"

        mock_run = mocker.patch(
            "build_harness.tools.git.subprocess.run", return_value=mock_result
        )

        _validate_git_version()

    def test_minimum_pass(self, mocker):
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_result.stdout = "git version 2.28"

        mock_run = mocker.patch(
            "build_harness.tools.git.subprocess.run", return_value=mock_result
        )

        _validate_git_version()

    def test_minimum_fail(self, mocker):
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_result.stdout = "git version 2.27.4"

        mock_run = mocker.patch(
            "build_harness.tools.git.subprocess.run", return_value=mock_result
        )

        with pytest.raises(GitError, match=r"^Incorrect git version must be"):
            _validate_git_version()


class TestValidateGit:
    def test_system_clean(self, mocker):
        mocker.patch("build_harness.tools.git._validate_git_version")
        mocker.patch(
            "build_harness.tools.git.shutil.which",
            return_value="/usr/bin/git",
        )

        validate_git(None)

    def test_system_bad(self, mocker):
        mocker.patch("build_harness.tools.git._validate_git_version")
        mocker.patch("build_harness.tools.git.shutil.which", return_value=None)

        with pytest.raises(
            GitNotFoundError, match=r"^Git not available on users PATH"
        ):
            validate_git(None)

    def test_user_precedence(self, mocker):
        mocker.patch("build_harness.tools.git._validate_git_version")
        mocker.patch(
            "build_harness.tools.git.shutil.which",
            return_value="/usr/bin/git",
        )
        mock_exists = mocker.patch(
            "build_harness.tools.git.os.path.exists", return_value=True
        )

        validate_git("some/other/path")

        mock_exists.assert_called_once_with("some/other/path")

    def test_user_clean(self, mocker):
        mocker.patch("build_harness.tools.git._validate_git_version")
        mocker.patch("build_harness.tools.git.shutil.which", return_value=None)
        mocker.patch(
            "build_harness.tools.git.os.path.exists", return_value=True
        )

        validate_git("some/other/path")

    def test_user_bad(self, mocker):
        mocker.patch("build_harness.tools.git._validate_git_version")
        mocker.patch("build_harness.tools.git.shutil.which", return_value=None)

        with pytest.raises(
            GitNotFoundError, match=r"^User specified git invalid"
        ):
            validate_git("some/other/path")


class SimpleTags(TagBase):
    def __init__(self, tag: str):
        super().__init__(tag)

    def __call__(self, repo: git.Repo, repo_dir: pathlib.Path):
        self._commit_file(repo_dir / "c1", repo)
        repo.create_tag(self.tag, message="default branch tag")
        self._commit_file(repo_dir / "c2", repo)


@contextlib.contextmanager
def temp_repo(
    repo_init: TagBase, initial_branch: str = "main"
) -> typing.Generator[git.Repo, None, None]:
    with tempfile.TemporaryDirectory() as dir:
        repo_path = pathlib.Path(dir)
        repo = git.Repo.init(str(repo_path), initial_branch=initial_branch)
        repo_init(repo, repo_path)

        yield repo, repo_path


class TestIsCommitTagged:
    def test_true(self):
        with temp_repo(SimpleTags("some_tag")) as (git_repo, repo_path):
            assert _is_commit_tagged(git_repo.commit("HEAD^"), git_repo)

    def test_false(self):
        with temp_repo(SimpleTags("some_tag")) as (git_repo, repo_path):
            assert not _is_commit_tagged(git_repo.head.commit, git_repo)


class TestParseDescribe:
    def test_semantic_tag(self):
        mock_describe = "3.1.4"

        result = _parse_describe(mock_describe)

        assert result == TagData(tag="3.1.4", offset=None)

    def test_semantic_tag_offset(self):
        mock_describe = "3.1.4-14-gc3ba625"

        result = _parse_describe(mock_describe)

        assert result == TagData(tag="3.1.4", offset="14")

    def test_pep440_tag_offset(self):
        mock_describe = "3!1.4.15.92a6.post5.dev4-14-gc3ba625"

        result = _parse_describe(mock_describe)

        assert result == TagData(tag="3!1.4.15.92a6.post5.dev4", offset="14")

    def test_no_match(self, mocker):
        mock_describe = "3!1.4.15.92a6.post5.dev4-some-stuff"

        # The regex pattern seems to be quite strong, so not an obvious path to an
        # error here. Just use a patch to force the error state.
        mocker.patch("build_harness.tools.git.re.search", return_value=None)

        with pytest.raises(TagDataError):
            _parse_describe(mock_describe)


class TestGetTagData:
    def test_semantic_tag(self):
        expected_tag_data = TagData(tag="1!2.3a4.dev6", offset=None)

        with temp_repo(TagOnHead("1!2.3a4.dev6")) as (git_repo, repo_path):
            result = get_tag_data(repo_path)

        assert result == expected_tag_data

    def test_dryrun_on_head(self):
        """Dryrun tag on HEAD gets used as-is."""
        expected_tag_data = TagData(tag="3.1+dryrun2")

        with temp_repo(FeatureDryrunTagOnHead("1!2.3a4.dev6")) as (
            git_repo,
            repo_path,
        ):
            result = get_tag_data(repo_path)

        assert result == expected_tag_data

    def test_dryrun_in_history(self):
        """Dryrun tags in commit history get ignored."""
        expected_tag_data = TagData(tag="1!2.3a4.dev6", offset="4")

        with temp_repo(FeatureDryrunTags("1!2.3a4.dev6")) as (
            git_repo,
            repo_path,
        ):
            result = get_tag_data(repo_path)

        assert result == expected_tag_data

    def test_nondefault_branch(self):
        expected_tag_data = TagData(tag="0.0.0", offset="1")

        with temp_repo(NoTags()) as (git_repo, repo_path):
            nb = git_repo.create_head("other_branch")
            git_repo.head.reference = nb
            git_repo.head.reset(index=True, working_tree=True)
            try:
                git_repo.delete_head(git_repo.heads.main)
            except AttributeError:
                # this exception is raised on an attempt to delete a head that
                # doesn't exist. this test is just trying to define the
                # appropriate entry state for the test, so just swallow this
                # error.
                pass

            result = get_tag_data(repo_path, default_branch_name="other_branch")

        assert result == expected_tag_data

    def test_semantic_tag_offset(self):
        expected_tag_data = TagData(tag="3.1.4", offset="2")
        with temp_repo(TagOnDefaultHeadOnFeature("3.1.4")) as (
            git_repo,
            repo_path,
        ):
            result = get_tag_data(repo_path)

        assert result == expected_tag_data

    def test_no_tag(self):
        default_branch = "main"
        expected_tag_data = TagData(tag="0.0.0", offset="1")

        with temp_repo(NoTags(), initial_branch=default_branch) as (
            git_repo,
            repo_path,
        ):
            result = get_tag_data(repo_path, default_branch_name=default_branch)

        assert result == expected_tag_data

    def test_bad_tag(self):
        with tempfile.TemporaryDirectory() as this_dir:
            mock_path = pathlib.Path(this_dir)

            with pytest.raises(GitRepoError, match=r"^Invalid git repository"):
                get_tag_data(mock_path)

    def test_git_command_error(self, caplog):
        with temp_repo(NoTags()) as (
            git_repo,
            repo_path,
        ):
            with caplog.at_level(logging.DEBUG):
                result = get_tag_data(repo_path)

            log_content = caplog.text

            assert "handling GitCommandError" in log_content
            assert result.tag == "0.0.0"
