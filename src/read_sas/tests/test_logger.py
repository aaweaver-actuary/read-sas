"""Test suite for the package logger.

import logging

LOGGING_LEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)
file_handler = logging.FileHandler("read_sas.log")
file_handler.setLevel(LOGGING_LEVEL)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
"""

from __future__ import annotations
from read_sas.src._logger import logger
import pytest
from pathlib import Path
import logging


def test_logger_file_creation(tmp_path: Path):
    """Test if the logger creates a log file."""
    log_file = tmp_path / "read_sas.log"
    logger.addHandler(logging.FileHandler(log_file))
    logger.info("Test log message")
    assert log_file.exists(), f"Log file {log_file} does not exist."


def test_logger_log_message(tmp_path: Path):
    """Test if the logger writes the correct message to the log file."""
    log_file = tmp_path / "read_sas.log"
    handler = logging.FileHandler(log_file)
    logger.addHandler(handler)
    logger.info("Test log message")
    handler.close()

    with Path(log_file).open("r") as f:
        log_content = f.read()

    assert (
        "Test log message" in log_content
    ), f"Expected to find 'Test log message' in [{log_content}]"


def test_logger_log_format(tmp_path: Path):
    """Test if the logger writes the log message in the correct format."""
    log_file = tmp_path / "read_sas.log"
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Test log message")
    handler.close()

    with Path(log_file).open("r") as f:
        log_content = f.read()

    assert "INFO" in log_content, f"Expected to find 'INFO' in [{log_content}]"
    assert (
        "Test log message" in log_content
    ), f"Expected to find 'Test log message' in [{log_content}]"


def test_logger_multiple_handlers(tmp_path: Path):
    """Test if the logger can handle multiple handlers."""
    log_file1 = tmp_path / "read_sas1.log"
    log_file2 = tmp_path / "read_sas2.log"
    handler1 = logging.FileHandler(log_file1)
    handler2 = logging.FileHandler(log_file2)
    logger.addHandler(handler1)
    logger.addHandler(handler2)
    logger.info("Test log message")
    handler1.close()
    handler2.close()

    with Path(log_file1).open("r") as f1, Path(log_file2).open("r") as f2:
        log_content1 = f1.read()
        log_content2 = f2.read()

    assert (
        "Test log message" in log_content1
    ), f"Expected to find 'Test log message' in [{log_content1}]"
    assert (
        "Test log message" in log_content2
    ), f"Expected to find 'Test log message' in [{log_content2}]"
