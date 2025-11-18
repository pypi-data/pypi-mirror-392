#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import logging
import pathlib
import subprocess
import sys
import typing

log = logging.getLogger(__name__)

CommandArgs = typing.List[str]


def run_command(
    command: CommandArgs, **kwargs: typing.Any
) -> subprocess.CompletedProcess:
    """
    Run a system command using ``subprocess.run``.

    Args:
        command: List of command and arguments.
        **kwargs: Optional arguments passed through to ``subprocess.run``.

    Returns:
        Subprocess results.
    """
    log.debug("command to run, {0}".format(str(command)))
    log.debug("command arguments, {0}".format(str(kwargs)))
    result = subprocess.run(command, **kwargs)

    return result


def run_command_sequence(sequence: typing.List[str]) -> None:
    """
    Run through a shell command sequence.

    Args:
        sequence: List of commands to be executed.
    """
    for this_command in sequence:
        response = run_command(this_command.split())


def create_venv() -> None:
    """Create virtual environment for new project."""
    venv_dir = pathlib.Path("{{ cookiecutter._venv_bin }}").parent
    commands = [
        "python3 -m venv {0}".format(venv_dir),
    ]
    if (
        # Jinja2 expressions in this string must not be split across lines.
        "{{ ('disable_bh_dependencies' not in cookiecutter) or (not cookiecutter.disable_bh_dependencies) }}"
        == "True"  # noqa: E501
    ):
        # default install build_harness utility
        commands += [
            "{{ cookiecutter._venv_bin }}/pip install build_harness",
        ]
    else:
        # assume build_harness utility has been installed externally
        log.debug(f"Assuming externally created venv, {venv_dir}")
        if not (venv_dir / "bin/build-harness").is_file():
            raise RuntimeError(
                "Build harness must be installed before bootstrap run "
                "disabling dependencies."
            )

    run_command_sequence(commands)


def verify_flit_project_summary() -> None:
    project_summary = "{{ cookiecutter.project_summary }}"

    if not project_summary.endswith("."):
        print(
            "ERROR: flit project summary must end with '.', {0}".format(
                project_summary
            )
        )
        sys.exit(1)


def verify_flit() -> None:
    verify_flit_project_summary()


def main() -> None:
    packaging_provider = "{{ cookiecutter.packaging_provider }}"

    if "{{ cookiecutter.enable_venv }}" == "True":
        # create virtual environment for new project
        create_venv()
    if packaging_provider == "flit":
        verify_flit()


if __name__ == "__main__":
    main()
