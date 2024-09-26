import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from read_sas.src._config import Config
from read_sas.src._n_gb_in_file import n_gb_in_file


@pytest.fixture
def mock_config():
    """Fixture to create a mock Config object with a logger."""
    mock = Mock(spec=Config)
    mock.logger = Mock()  # Mock logger for error handling
    return mock


@pytest.mark.parametrize(
    "filepath, file_size_bytes, expected_size_gb",
    [
        ("file.txt", 1_000_000_000, 1.0),  # 1 GB file
        ("file.txt", 500_000_000, 0.5),  # 0.5 GB file
        (Path("file.txt"), 2_000_000_000, 2.0),  # 2 GB file as Path object
        (Path("large_file.txt"), 10_000_000_000, 10.0),  # 10 GB file
    ],
)
@patch("pathlib.Path.stat")
def test_n_gb_in_file_valid_inputs(
    mock_stat, mock_config, filepath, file_size_bytes, expected_size_gb, capsys
):
    """Parameterized test for the `n_gb_in_file` function with valid inputs.

    Checks that the function returns the correct file size in GB.
    """
    # Mock the file size using stat
    mock_stat.return_value.st_size = file_size_bytes

    # Call the function
    result = n_gb_in_file(filepath, config=mock_config)

    # Check that the correct size in GB is returned
    assert result == expected_size_gb, f"Expected: {expected_size_gb}, Got: {result}"

    # Capture the printed output from the `timer` decorator
    captured = capsys.readouterr()

    # Ensure execution time is printed
    assert (
        "Execution time" in captured.out
    ), f"Expected 'Execution time' in output, Got: {captured.out}"


@pytest.mark.parametrize(
    "invalid_filepath",
    [
        (123),  # Invalid type: integer
        (None),  # Invalid type: None
        ({}),  # Invalid type: dict
    ],
)
@patch(
    "pathlib.Path.stat", side_effect=FileNotFoundError
)  # Ensure stat doesn't get called for invalid cases
def test_n_gb_in_file_invalid_inputs(mock_config, invalid_filepath):
    """Test for invalid inputs to `n_gb_in_file`.

    Expects a ValueError and logs an error when the input type is neither `str` nor `Path`.
    """
    with pytest.raises(ValueError):
        n_gb_in_file(invalid_filepath, config=mock_config)

    # Check that an error was logged
    mock_config.logger.error.assert_called_once_with(
        f"Invalid type for filepath: {type(invalid_filepath)}, expected str or Path."
    )


@pytest.mark.parametrize(
    "filepath",
    [
        ("nonexistent_file.txt")  # File does not exist, expect FileNotFoundError
    ],
)
@patch("pathlib.Path.stat", side_effect=FileNotFoundError)
def test_n_gb_in_file_file_not_found(mock_config, filepath):
    """Test that `n_gb_in_file` raises an appropriate exception when the file does not exist."""
    with pytest.raises(FileNotFoundError):
        n_gb_in_file(filepath, config=mock_config)

    # Ensure no logging for non-existent files, this should raise directly
    mock_config.logger.error.assert_not_called()
