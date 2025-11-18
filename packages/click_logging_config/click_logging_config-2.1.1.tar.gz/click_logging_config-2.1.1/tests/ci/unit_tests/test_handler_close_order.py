#
#  Copyright (c) 2025 Russell Smiley
#
#  This file is part of click_logging_config.
#
#  You should have received a copy of the MIT License along with click_logging_config.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Tests for handler close order bug fix."""

import logging
import unittest.mock as mock

import pytest

from click_logging_config._logging import LoggingConfiguration, LoggingState
from tests.ci.support.directory import change_directory  # noqa: F401


def test_file_handler_removed_before_close():
    """Test that file handler is removed from logger before being closed.

    This prevents "I/O operation on closed file" errors that occur when
    a handler is closed while still attached to the logger.
    """
    config = LoggingConfiguration.model_validate(
        {
            "enable_file_logging": True,
            "enable_console_logging": False,
            "log_level": "info",
        }
    )

    with change_directory():
        logging_state = LoggingState(config)

        # Verify handler is attached
        assert logging_state._rotation_handler is not None
        root_logger = logging.getLogger()
        assert logging_state._rotation_handler in root_logger.handlers

        # Spy on the handler methods to track call order
        original_close = logging_state._rotation_handler.close
        original_flush = logging_state._rotation_handler.flush

        call_order = []

        def tracked_close():
            call_order.append("close")
            # Verify handler has been removed before close is called
            assert (
                logging_state._rotation_handler not in root_logger.handlers
            ), "Handler should be removed from logger before close() is called"
            original_close()

        def tracked_flush():
            call_order.append("flush")
            original_flush()

        # Patch the methods
        with mock.patch.object(
            logging_state._rotation_handler, "close", tracked_close
        ):
            with mock.patch.object(
                logging_state._rotation_handler, "flush", tracked_flush
            ):
                # Disable file logging - this triggers the cleanup code
                logging_state.configuration.enable_file_logging = False
                logging_state.set_logging_state()

        # Verify operations occurred in correct order
        # Note: Additional flushes may occur during cleanup, but we verify
        # that flush and close were called, and close came after flush
        assert "flush" in call_order
        assert "close" in call_order
        flush_index = call_order.index("flush")
        close_index = call_order.index("close")
        assert close_index > flush_index, (
            "close() should be called after flush()"
        )
        assert logging_state._rotation_handler is None


def test_console_handler_removed_before_close():
    """Test that console handler is removed from logger before being closed.

    This prevents "I/O operation on closed file" errors that occur when
    a handler is closed while still attached to the logger.
    """
    config = LoggingConfiguration.model_validate(
        {
            "enable_file_logging": False,
            "enable_console_logging": True,
            "log_level": "info",
        }
    )

    with change_directory():
        logging_state = LoggingState(config)

        # Verify handler is attached
        assert logging_state._console_handler is not None
        root_logger = logging.getLogger()
        assert logging_state._console_handler in root_logger.handlers

        # Spy on the handler methods to track call order
        original_close = logging_state._console_handler.close
        original_flush = logging_state._console_handler.flush

        call_order = []

        def tracked_close():
            call_order.append("close")
            # Verify handler has been removed before close is called
            assert logging_state._console_handler not in root_logger.handlers, (
                "Handler should be removed from logger before close() is called"
            )
            original_close()

        def tracked_flush():
            call_order.append("flush")
            original_flush()

        # Patch the methods
        with mock.patch.object(
            logging_state._console_handler, "close", tracked_close
        ):
            with mock.patch.object(
                logging_state._console_handler, "flush", tracked_flush
            ):
                # Disable console logging - this triggers the cleanup code
                logging_state.configuration.enable_console_logging = False
                logging_state.set_logging_state()

        # Verify operations occurred in correct order
        assert call_order == ["flush", "close"]
        assert logging_state._console_handler is None


def test_logging_during_file_handler_removal_no_error():
    """Test that logging during handler removal doesn't cause errors.

    When a handler is closed before being removed, any logging that occurs
    during the removal process can cause "I/O operation on closed file" errors.
    """
    config = LoggingConfiguration.model_validate(
        {
            "enable_file_logging": True,
            "enable_console_logging": False,
            "log_level": "debug",
        }
    )

    with change_directory():
        logging_state = LoggingState(config)
        log = logging.getLogger(__name__)

        # Log a message while handler is active (should work)
        log.info("Message with handler active")

        # Patch removeHandler to trigger logging during removal
        original_remove = logging.getLogger().removeHandler

        def remove_with_logging(handler):
            # This simulates logging that might occur during handler removal
            # If handler is closed first, this will fail
            log.debug("Logging during handler removal")
            original_remove(handler)

        with mock.patch.object(
            logging.getLogger(), "removeHandler", remove_with_logging
        ):
            # This should not raise "I/O operation on closed file"
            logging_state.configuration.enable_file_logging = False
            logging_state.set_logging_state()

        assert logging_state._rotation_handler is None


def test_logging_during_console_handler_removal_no_error():
    """Test that logging during console handler removal doesn't cause errors.

    When a handler is closed before being removed, any logging that occurs
    during the removal process can cause "I/O operation on closed file" errors.
    """
    config = LoggingConfiguration.model_validate(
        {
            "enable_file_logging": False,
            "enable_console_logging": True,
            "log_level": "debug",
        }
    )

    with change_directory():
        logging_state = LoggingState(config)
        log = logging.getLogger(__name__)

        # Log a message while handler is active (should work)
        log.info("Message with handler active")

        # Patch removeHandler to trigger logging during removal
        original_remove = logging.getLogger().removeHandler

        def remove_with_logging(handler):
            # This simulates logging that might occur during handler removal
            # If handler is closed first, this will fail
            log.debug("Logging during handler removal")
            original_remove(handler)

        with mock.patch.object(
            logging.getLogger(), "removeHandler", remove_with_logging
        ):
            # This should not raise "I/O operation on closed file"
            logging_state.configuration.enable_console_logging = False
            logging_state.set_logging_state()

        assert logging_state._console_handler is None


def test_file_handler_close_not_called_on_closed_handler():
    """Test that we don't try to close an already closed handler.

    This is a safety check to ensure the handler lifecycle is properly managed.
    """
    config = LoggingConfiguration.model_validate(
        {
            "enable_file_logging": True,
            "enable_console_logging": False,
            "log_level": "info",
        }
    )

    with change_directory():
        logging_state = LoggingState(config)

        # Track if close is called
        close_call_count = 0
        original_close = logging_state._rotation_handler.close

        def tracked_close():
            nonlocal close_call_count
            close_call_count += 1
            original_close()

        with mock.patch.object(
            logging_state._rotation_handler, "close", tracked_close
        ):
            # Disable file logging
            logging_state.configuration.enable_file_logging = False
            logging_state.set_logging_state()

            # Disable again - should not try to close again
            logging_state.configuration.enable_file_logging = False
            logging_state.set_logging_state()

        # Close should only be called once
        assert close_call_count == 1
