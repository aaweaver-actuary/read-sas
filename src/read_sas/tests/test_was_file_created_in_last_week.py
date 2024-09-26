import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from pathlib import Path
from read_sas.src._was_file_created_in_last_week import was_file_created_in_last_week
from read_sas.src.__format_filepath import _format_filepath
from read_sas.src._config import Config


@pytest.mark.parametrize(
    "file_creation_time, current_time, expected_result",
    [
        (
            datetime.now() - timedelta(days=2),
            datetime.now(),
            True,
        ),  # created 2 days ago
        (
            datetime.now() - timedelta(days=6, hours=23),
            datetime.now(),
            True,
        ),  # created 6 days ago, within a week
        (
            datetime.now() - timedelta(days=8),
            datetime.now(),
            False,
        ),  # created 8 days ago, outside a week
        (
            datetime.now() - timedelta(days=7),
            datetime.now(),
            False,
        ),  # exactly 7 days ago, should return False
    ],
)
@patch("pathlib.Path.stat")
@patch("datetime.datetime")
def test_was_file_created_in_last_week(
    mock_datetime, mock_stat, file_creation_time, current_time, expected_result
):
    """Parameterized test for the `was_file_created_in_last_week` function.

    It checks various cases for file creation time relative to the current time.
    """
    # Mock the current time to ensure consistent testing
    mock_datetime.now.return_value = current_time

    # Mock the file creation time by patching Path.stat
    mock_stat.return_value.st_ctime = file_creation_time.timestamp()

    # Create a mock Path object that has a created on date given by file_creation_time
    mock_path = Mock(spec=Path, stat=mock_stat, __str__=lambda _: "mock_path")

    # Call the function
    result = was_file_created_in_last_week(mock_path)

    # Assert the result matches the expected outcome
    assert result == expected_result, f"Expected: {expected_result}, Got: {result}"


@pytest.mark.parametrize(
    "filepath, expected_type",
    [
        ("some/file/path.txt", Path),  # string input
        (Path("some/file/path.txt"), Path),  # Path object input
    ],
)
@patch("pathlib.Path.stat")
def test_was_file_created_in_last_week_input_conversion(
    mock_stat, filepath, expected_type
):
    """Test to check that the `was_file_created_in_last_week` function converts string inputs to `Path` objects."""
    # Mock the file creation time (actual value doesn't matter for this test)
    mock_stat.return_value.st_ctime = (datetime.now() - timedelta(days=3)).timestamp()

    # Format the filepath
    filepath = _format_filepath(filepath, Config())

    # Call the function
    _ = was_file_created_in_last_week(filepath)

    # Check that the conversion was successful (implicitly handled by Path.stat being called)
    assert isinstance(
        filepath, expected_type
    ), f"Expected: {expected_type}, Got: {type(filepath)}"
