import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import pyreadstat
from read_sas.src._n_rows_in_sas7bdat import n_rows_in_sas7bdat
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
@patch("read_sas.src.__format_filepath._format_filepath")  # Mock filepath conversion
def test_n_rows_in_sas7bdat_valid_inputs(
    mock_format_filepath,
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
    mock_format_filepath.return_value = Path(filepath)

    # Mock the pyreadstat.read_sas7bdat to return the mock meta
    mock_read_sas7bdat.return_value = (None, mock_meta)

    # Call the function
    result = n_rows_in_sas7bdat(filepath, column_list)

    # Check that the number of rows returned is correct
    assert result == expected_rows, f"Expected: {expected_rows}, Got: {result}"

    # Capture the printed output from the `timer` decorator
    captured = capsys.readouterr()

    # Ensure execution time is printed
    assert (
        "Execution time" in captured.out
    ), f"Expected 'Execution time' in output, Got: {captured.out}"

    # Ensure _format_filepath was called with the correct arguments
    mock_format_filepath.assert_called_once_with(filepath, mock_config)

    # Ensure pyreadstat.read_sas7bdat was called with the correct parameters
    mock_read_sas7bdat.assert_called_once_with(
        mock_format_filepath.return_value,
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
@patch("read_sas.src.__format_filepath._format_filepath")  # Mock filepath conversion
def test_n_rows_in_sas7bdat_file_not_found(
    mock_format_filepath, mock_read_sas7bdat, filepath, column_list, mock_config
):
    """Test that `n_rows_in_sas7bdat` raises appropriate exceptions when the file does not exist."""
    # Mock the _format_filepath to return the same filepath
    mock_format_filepath.return_value = Path(filepath)

    # Expect a FileNotFoundError to be raised
    with pytest.raises(FileNotFoundError):
        n_rows_in_sas7bdat(filepath, column_list)

    # Ensure _format_filepath was called correctly
    mock_format_filepath.assert_called_once_with(filepath, mock_config)

    # Ensure pyreadstat.read_sas7bdat was called with the correct parameters
    mock_read_sas7bdat.assert_called_once_with(
        mock_format_filepath.return_value,
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
@patch("read_sas.src.__format_filepath._format_filepath")  # Mock filepath conversion
def test_n_rows_in_sas7bdat_invalid_column(
    mock_format_filepath, mock_read_sas7bdat, filepath, column_list, mock_config
):
    """Test that `n_rows_in_sas7bdat` raises a ValueError when invalid columns are selected."""
    # Mock the _format_filepath to return the same filepath
    mock_format_filepath.return_value = Path(filepath)

    # Expect a ValueError to be raised for invalid columns
    with pytest.raises(ValueError):
        n_rows_in_sas7bdat(filepath, column_list)

    # Ensure _format_filepath was called correctly
    mock_format_filepath.assert_called_once_with(filepath, mock_config)

    # Ensure pyreadstat.read_sas7bdat was called with the correct parameters
    mock_read_sas7bdat.assert_called_once_with(
        mock_format_filepath.return_value,
        disable_datetime_conversion=True,
        usecols=column_list,
        metadataonly=True,
    )
