#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pathlib
import typing

import pytest

from tests.ci.support.project_context import ProjectData, run_cookiecutter


@pytest.fixture(scope="module")
def flit_gitlabci_project():
    project_name = "test-flit-gitlabci"
    project_slug = project_name.replace(" ", "_").replace("-", "_")
    context_configuration = {
        "disable_bh_dependencies": True,
        "packaging_provider": "flit",
        "pipeline_provider": "gitlabci",
        "project_name": project_name,
    }
    with run_cookiecutter(
        context_configuration, project_name, enable_venv=False
    ) as (
        this_context,
        captured_stdio,
    ):
        temp_path = this_context.temp_path

        expected_files: typing.List[pathlib.Path] = [
            temp_path / project_slug / "pyproject.toml",
            temp_path / project_slug / ".gitlab-ci.yml",
        ]
        file_contents = dict()
        for this_file in expected_files:
            if this_file.is_file():
                with this_file.open("r") as f:
                    file_contents[this_file.name] = f.read()
            else:
                file_contents[this_file.name] = None

    result = ProjectData(
        captured_io=captured_stdio,
        file_contents=file_contents,
        project_name=project_name,
    )

    return result


class TestFlitGitlabciCookiecutter:
    def test_flit(self, flit_gitlabci_project):
        if not flit_gitlabci_project.file_contents["pyproject.toml"]:
            flit_gitlabci_project.captured_io.err.seek(0)
            flit_gitlabci_project.captured_io.out.seek(0)

            print(flit_gitlabci_project.captured_io.out.read())
            print(flit_gitlabci_project.captured_io.err.read())
            pytest.fail("pyproject.toml file not found")

        assert (
            'requires = ["flit_core'
            in flit_gitlabci_project.file_contents["pyproject.toml"]
        )

    def test_gitlabci(self, flit_gitlabci_project):
        if not flit_gitlabci_project.file_contents[".gitlab-ci.yml"]:
            flit_gitlabci_project.captured_io.err.seek(0)
            flit_gitlabci_project.captured_io.out.seek(0)

            print(flit_gitlabci_project.captured_io.out.read())
            print(flit_gitlabci_project.captured_io.err.read())
            pytest.fail(".gitlab-ci.yml file not found")
