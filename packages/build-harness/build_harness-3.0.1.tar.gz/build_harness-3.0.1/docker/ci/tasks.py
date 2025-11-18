#
#  Copyright (c) 2023 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#
import os.path

import invoke

BUILD_DOCKERFILE = "Dockerfile-apt-lock"


def _find_container_tool(
    context: invoke.Context,
) -> str:
    for this_command in ["nerdctl", "docker", "podman"]:
        try:
            context.run(f"{this_command} --version")
            return this_command
        except invoke.exceptions.UnexpectedExit:
            pass

    raise FileNotFoundError("No container tool found")


@invoke.task
def generate_lockfile(
    context: invoke.Context,
    target: str,
) -> None:
    lock_file = f"{target}.lock"
    src_file = f"{target}.txt"
    docker_image = f"{target}".replace("_", "-")

    assert os.path.isfile(src_file), f"File {src_file} does not exist"

    # make sure lock file does not exist
    try:
        os.remove(lock_file)
    except OSError:
        pass

    container_command = _find_container_tool(context)

    context.run(
        (
            f"{container_command} "
            "build "
            f"--build-arg requirements_src={target} "
            "--no-cache "
            f"-t {docker_image} "
            f"-f {BUILD_DOCKERFILE} "
            "."
        ),
        echo=True,
    )
    context.run(
        (
            f"{container_command} "
            "run "
            "--rm "
            "-v $(PWD):/media "
            "-w /media "
            f"{docker_image}"
        ),
        echo=True,
    )
    assert os.path.isfile(lock_file), f"File {lock_file} has not been generated"
