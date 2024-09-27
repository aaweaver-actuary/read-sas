import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import pyreadstat
from read_sas.src._n_rows_in_sas7bdat import n_rows_in_sas7bdat
from read_sas.src.__format_filepath import _format_filepath
from read_sas.src._config import Config


@pytest.fixture
def mock_meta():
    """Fixture to create a mock metadata object."""
    mock = Mock()
    mock.number_rows = 1000  # default number of rows for the mock
    return mock


@pytest.fixture
def mock_config():
    """Fixture to create a mock Config object."""
    return Mock(spec=Config)


@pytest.mark.parametrize(
    "filepath, column_list, expected_rows",
    [
        ("data/file.sas7bdat", None, 1000),  # No columns selected, full file
        (Path("data/file.sas7bdat"), None, 1000),  # Path object as input
        ("data/file.sas7bdat", ["col1", "col2"], 1000),  # Specific columns selected
    ],
)
@patch("pyreadstat.read_sas7bdat")
def test_n_rows_in_sas7bdat_valid_inputs(
    mock_read_sas7bdat,
    mock_meta,
    filepath,
    column_list,
    expected_rows,
    capsys,
    mock_config,
):
    """Parameterized test for the `n_rows_in_sas7bdat` function with valid inputs.

    It checks that the function returns the correct number of rows.
    """
    # Mock the output of _format_filepath to return the filepath as Path object
    filepath = _format_filepath(Path(filepath), mock_config)

    # Mock the pyreadstat.read_sas7bdat to return the mock meta
    mock_read_sas7bdat.return_value = (None, mock_meta)

    # Call the function
    result = n_rows_in_sas7bdat(filepath, mock_config, column_list)

    # Check that the number of rows returned is correct
    assert result == expected_rows, f"Expected: {expected_rows}, Got: {result}"

    # Capture the printed output from the `timer` decorator
    captured = capsys.readouterr()

    # Ensure execution time is printed
    assert (
        "Execution time" in captured.out
    ), f"Expected 'Execution time' in output, Got: {captured.out}"

    # Ensure pyreadstat.read_sas7bdat was called with the correct parameters
    mock_read_sas7bdat.assert_called_once_with(
        filepath,
        disable_datetime_conversion=True,
        usecols=column_list,
        metadataonly=True,
    )


@pytest.mark.parametrize(
    "filepath, column_list",
    [
        ("data/file.sas7bdat", ["col1", "col2"]),  # With selected columns
        ("nonexistent_file.sas7bdat", None),  # File does not exist
    ],
)
@patch("pyreadstat.read_sas7bdat", side_effect=FileNotFoundError)
def test_n_rows_in_sas7bdat_file_not_found(
    mock_read_sas7bdat, filepath, column_list, mock_config
):
    """Test that `n_rows_in_sas7bdat` raises appropriate exceptions when the file does not exist."""
    # Mock the _format_filepath to return the same filepath
    filepath = _format_filepath(Path(filepath), mock_config)

    # Expect a FileNotFoundError to be raised
    with pytest.raises(FileNotFoundError):
        n_rows_in_sas7bdat(filepath, mock_config, column_list)

    # Ensure pyreadstat.read_sas7bdat was called with the correct parameters
    mock_read_sas7bdat.assert_called_once_with(
        filepath,
        disable_datetime_conversion=True,
        usecols=column_list,
        metadataonly=True,
    )


@pytest.mark.parametrize(
    "filepath, column_list",
    [
        ("data/file.sas7bdat", None),  # Full file
        ("data/file.sas7bdat", ["invalid_col"]),  # Invalid column in column list
    ],
)
@patch("pyreadstat.read_sas7bdat", side_effect=ValueError)
def test_n_rows_in_sas7bdat_invalid_column(
    mock_read_sas7bdat, filepath, column_list, mock_config
):
    """Test that `n_rows_in_sas7bdat` raises a ValueError when invalid columns are selected."""
    # Mock the _format_filepath to return the same filepath
    filepath = _format_filepath(Path(filepath), mock_config)

    # Expect a ValueError to be raised for invalid columns
    with pytest.raises(ValueError):
        n_rows_in_sas7bdat(filepath, mock_config, column_list)

    # Ensure pyreadstat.read_sas7bdat was called with the correct parameters
    mock_read_sas7bdat.assert_called_once_with(
        filepath,
        disable_datetime_conversion=True,
        usecols=column_list,
        metadataonly=True,
    )
