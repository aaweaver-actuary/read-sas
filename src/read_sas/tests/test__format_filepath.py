import pytest
from unittest.mock import Mock
from pathlib import Path
from read_sas.src.__format_filepath import _format_filepath


@pytest.mark.parametrize(
    "filepath, expected_result",
    [
        ("file.txt", Path("file.txt")),  # string filepath
        (Path("file.txt"), Path("file.txt")),  # Path object
        (
            "/absolute/path/to/file.txt",
            Path("/absolute/path/to/file.txt"),
        ),  # absolute path as string
        (
            Path("/absolute/path/to/file.txt"),
            Path("/absolute/path/to/file.txt"),
        ),  # absolute path as Path
    ],
)
def test_format_filepath_valid_inputs(filepath, expected_result):
    """Parameterized test for the `_format_filepath` function.

    Covers valid cases where the input is either a string or a Path object.
    """
    result = _format_filepath(filepath)
    assert result == expected_result, f"Expected: {expected_result}, Got: {result}"


@pytest.mark.parametrize(
    "invalid_filepath",
    [
        (123),  # integer
        (None),  # None type
        ({}),  # dict
        ([]),  # list
    ],
)
def test_format_filepath_invalid_inputs(invalid_filepath):
    """Parameterized test for invalid inputs to `_format_filepath`.

    Expects a ValueError and a log message when the input is neither a string nor a Path object.
    """
    with pytest.raises(ValueError):
        _format_filepath(invalid_filepath)
