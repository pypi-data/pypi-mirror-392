#
#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import logging

import pytest

import build_harness.commands.build_harness_group


@pytest.fixture
def mock_sysargv():
    build_harness.commands.build_harness_group.sys.argv = [
        "/some/conftest/path/build-harness"
    ]


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration between tests to prevent handler contamination."""
    # Get the root logger
    root_logger = logging.getLogger()

    # Store initial handlers
    initial_handlers = root_logger.handlers[:]

    yield

    # After test: remove any handlers that were added and close them
    for handler in root_logger.handlers[:]:
        if handler not in initial_handlers:
            handler.close()
            root_logger.removeHandler(handler)

    # Also clean up any handlers on specific loggers
    for name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(name)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
