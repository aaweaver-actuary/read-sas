import pytest
from unittest.mock import Mock
from pathlib import Path
from read_sas.src._config import Config
from read_sas.src.__format_filepath import _format_filepath


@pytest.fixture
def mock_config():
    """Fixture to create a mock configuration object."""
    mock = Mock(spec=Config)
    mock.logger = Mock()  # Mock logger to handle error logging
    return mock


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
def test_format_filepath_valid_inputs(mock_config, filepath, expected_result):
    """Parameterized test for the `_format_filepath` function.

    Covers valid cases where the input is either a string or a Path object.
    """
    result = _format_filepath(filepath, config=mock_config)
    assert result == expected_result, f"Expected: {expected_result}, Got: {result}"
    mock_config.logger.error.assert_not_called()  # Ensure no logging for valid cases


@pytest.mark.parametrize(
    "invalid_filepath",
    [
        (123),  # integer
        (None),  # None type
        ({}),  # dict
        ([]),  # list
    ],
)
def test_format_filepath_invalid_inputs(mock_config, invalid_filepath):
    """Parameterized test for invalid inputs to `_format_filepath`.

    Expects a ValueError and a log message when the input is neither a string nor a Path object.
    """
    with pytest.raises(ValueError):
        _format_filepath(invalid_filepath, config=mock_config)

    # Check that an error was logged
    mock_config.logger.error.assert_called_once_with(
        f"Expected either a `str` or a `pathlib.Path` object for `filepath`, got: {type(invalid_filepath)}"
    )
