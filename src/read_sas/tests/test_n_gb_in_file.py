import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from read_sas.src._n_gb_in_file import n_gb_in_file


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
    mock_stat, filepath, file_size_bytes, expected_size_gb, capsys
):
    """Parameterized test for the `n_gb_in_file` function with valid inputs.

    Checks that the function returns the correct file size in GB.
    """
    # Mock the file size using stat
    mock_stat.return_value.st_size = file_size_bytes

    # Call the function
    result = n_gb_in_file(filepath)

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
def test_n_gb_in_file_invalid_inputs(invalid_filepath):
    """Test for invalid inputs to `n_gb_in_file`.

    Expects a ValueError and logs an error when the input type is neither `str` nor `Path`.
    """
    with pytest.raises(ValueError):
        n_gb_in_file(invalid_filepath)


@pytest.mark.parametrize(
    "filepath",
    [
        ("nonexistent_file.txt")  # File does not exist, expect FileNotFoundError
    ],
)
def test_n_gb_in_file_file_not_found(filepath):
    """Test that `n_gb_in_file` raises an appropriate exception when the file does not exist."""
    with pytest.raises(FileNotFoundError):
        n_gb_in_file(filepath)
