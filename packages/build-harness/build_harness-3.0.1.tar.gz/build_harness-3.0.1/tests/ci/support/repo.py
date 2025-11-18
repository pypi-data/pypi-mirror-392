#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#
import abc
import pathlib

import git


class TagBase(metaclass=abc.ABCMeta):
    def __init__(self, tag: str):
        self.tag = tag

    def _commit_file(self, file_path: pathlib.Path, repo: git.Repo) -> None:
        filename = str(file_path)
        open(filename, "wb").close()
        repo.index.add([filename])
        repo.index.commit(filename)

    @abc.abstractmethod
    def __call__(self, repo: git.Repo, repo_dir: pathlib.Path) -> None:
        return


class NoTags(TagBase):
    def __init__(self):
        super().__init__("no_tag")

    def __call__(self, repo: git.Repo, repo_dir: pathlib.Path) -> None:
        filename = repo_dir / "c1"
        self._commit_file(filename, repo)


class TagOnHead(TagBase):
    def __init__(self, tag: str):
        super().__init__(tag)

    def __call__(self, repo: git.Repo, repo_dir: pathlib.Path) -> None:
        filename = repo_dir / "c1"
        self._commit_file(filename, repo)
        repo.create_tag(self.tag, message="default branch tag")


class TagOnDefaultHeadOnFeature(TagBase):
    def __init__(self, tag: str):
        super().__init__(tag)

    def __call__(self, repo: git.Repo, repo_dir: pathlib.Path) -> None:
        self._commit_file(repo_dir / "c1", repo)
        repo.create_tag(self.tag, message="default branch tag")
        self._commit_file(repo_dir / "c2", repo)
        nb = repo.create_head("feature")
        repo.head.reference = nb
        repo.head.reset(index=True, working_tree=True)

        assert repo.active_branch.name == "feature"

        self._commit_file(repo_dir / "fc1", repo)


class FeatureDryrunTagOnHead(TagBase):
    def __init__(self, tag: str):
        super().__init__(tag)

    def __call__(self, repo: git.Repo, repo_dir: pathlib.Path) -> None:
        self._commit_file(repo_dir / "c1", repo)
        repo.create_tag(self.tag, message="default branch tag")
        self._commit_file(repo_dir / "c2", repo)
        nb = repo.create_head("feature")
        repo.head.reference = nb
        repo.head.reset(index=True, working_tree=True)

        assert repo.active_branch.name == "feature"

        self._commit_file(repo_dir / "fc1", repo)
        repo.create_tag("3.1+dryrun", message="feature branch dryrun")
        self._commit_file(repo_dir / "fc2", repo)
        repo.create_tag("3.1+dryrun2", message="feature branch dryrun 2")


class FeatureDryrunTags(TagBase):
    def __init__(self, tag: str):
        super().__init__(tag)

    def __call__(self, repo: git.Repo, repo_dir: pathlib.Path) -> None:
        self._commit_file(repo_dir / "c1", repo)
        repo.create_tag(self.tag, message="default branch tag")
        self._commit_file(repo_dir / "c2", repo)
        nb = repo.create_head("feature")
        nb.commit = repo.head.commit
        repo.head.reference = nb
        repo.head.reset(index=True, working_tree=True)

        assert repo.active_branch.name == "feature"

        self._commit_file(repo_dir / "fc1", repo)
        repo.create_tag("3.1+dryrun", message="feature branch dryrun")
        self._commit_file(repo_dir / "fc2", repo)
        repo.create_tag("3.1+dryrun2", message="feature branch dryrun 2")
        self._commit_file(repo_dir / "fc3", repo)
