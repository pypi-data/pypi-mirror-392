#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Common constants for command definitions."""

import enum
import pathlib

from click_logging_config.parameters import LoggingConfiguration

DEFAULT_PROJECT_PATH = "."

DEFAULT_CONSOLE_LOGGING_ENABLED = False
DEFAULT_FILE_LOGGING_ENABLED = True
DEFAULT_FILE_ROTATION_BACKUPS = 10
DEFAULT_FILE_ROTATION_SIZE_MB = 1
DEFAULT_LOG_FILE = pathlib.Path("build_harness.log")
DEFAULT_LOG_LEVEL = "warning"

DEFAULT_BUILDHARNESS_LOGCONFIG = LoggingConfiguration.parse_obj(
    {
        "enable_console_logging": DEFAULT_CONSOLE_LOGGING_ENABLED,
        "enable_file_logging": DEFAULT_FILE_LOGGING_ENABLED,
        "file_logging": {
            "file_rotation_size_megabytes": DEFAULT_FILE_ROTATION_SIZE_MB,
            "log_file_path": DEFAULT_LOG_FILE,
            "max_rotation_backup_files": DEFAULT_FILE_ROTATION_BACKUPS,
        },
        "log_level": DEFAULT_LOG_LEVEL,
    }
)


@enum.unique
class PublishOptions(enum.Enum):
    """Enumeration of artifact publish options."""

    yes = enum.auto()
    no = enum.auto()
    dryrun = enum.auto()
    test = enum.auto()
