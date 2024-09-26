import pytest
from unittest.mock import Mock
from read_sas.src._config import Config
from read_sas.src.__calculate_chunk_size import _calculate_chunk_size


@pytest.fixture
def mock_config():
    """Fixture to create a mock configuration object with a default chunk size in GB."""
    mock = Mock(spec=Config)
    mock.chunk_size_in_gb = 0.1  # default chunk size for the mock
    return mock


@pytest.mark.parametrize(
    "n_rows_in_file, file_size_in_gb, chunk_size_in_gb, expected_chunk_size",
    [
        (1000, 1.0, None, 100),  # default config chunk size
        (1000, 2.0, 0.5, 250),  # non-default chunk size
        (5000, 1.0, 0.1, 500),  # larger file, small chunk size
        (1000, 1.0, None, 100),  # using default config chunk size
        (1000, 0.5, 0.2, 400),  # smaller file size, non-default chunk size
        (1000, 2.0, None, 50),  # large file, default chunk size
    ],
)
def test_calculate_chunk_size(
    mock_config, n_rows_in_file, file_size_in_gb, chunk_size_in_gb, expected_chunk_size
):
    """
    Parameterized test for the `_calculate_chunk_size` function.
    Covers edge cases like 0 rows, small and large file sizes, and using default config values.
    """
    # Override config.chunk_size_in_gb if chunk_size_in_gb is provided
    if chunk_size_in_gb is None:
        mock_config.chunk_size_in_gb = 0.1  # Default value for the mock config

    result = _calculate_chunk_size(
        config=mock_config,
        n_rows_in_file=n_rows_in_file,
        file_size_in_gb=file_size_in_gb,
        chunk_size_in_gb=chunk_size_in_gb,
    )
    assert (
        result == expected_chunk_size
    ), f"Expected: {expected_chunk_size}, Got: {result}"


@pytest.mark.parametrize(
    "n_rows_in_file, file_size_in_gb, chunk_size_in_gb",
    [
        (1000, 0, None),  # division by zero test
        (1000, 1.0, -0.5),  # negative chunk size
        (0, 1.0, 0.1),  # no rows in file
        (1000, 1.0, 0.0),  # chunk size of zero
    ],
)
def test_calculate_chunk_size_invalid_inputs(
    mock_config, n_rows_in_file, file_size_in_gb, chunk_size_in_gb
):
    """
    Test for invalid inputs such as file size of zero or negative chunk size.
    These should raise appropriate errors (ValueError, ZeroDivisionError).
    """
    with pytest.raises((ZeroDivisionError, ValueError)):
        _calculate_chunk_size(
            config=mock_config,
            n_rows_in_file=n_rows_in_file,
            file_size_in_gb=file_size_in_gb,
            chunk_size_in_gb=chunk_size_in_gb,
        )
