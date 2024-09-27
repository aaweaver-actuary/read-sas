import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import polars as pl
from read_sas.src._sas_reader import sas_reader
import pandas as pd
import numpy as np


@pytest.fixture
def mock_config():
    """Fixture to create a mock Config object."""
    mock = Mock()
    mock.logger = Mock()  # Mock the logger
    mock.disable_datetime_conversion = True
    mock.use_multiprocessing = True
    mock.num_processes = None
    mock.chunk_size_in_gb = 1.0
    return mock


@pytest.fixture
def mock_formatter():
    """Fixture to create a mock formatter function that returns the LazyFrame unchanged."""
    return Mock(side_effect=lambda df: df)


@pytest.fixture
def lazyframe():
    """Fixture to create a mock polars LazyFrame."""
    df = pd.DataFrame(
        {
            "col1": np.random.default_rng(42).integers(0, 100, 1_000_000),
            "col2": np.random.default_rng(42).normal(0, 1, 1_000_000),
        }
    )
    return pl.from_pandas(df).lazy()


@pytest.mark.parametrize(
    "num_chunks, should_raise",
    [
        (3, False),  # Successfully process all chunks
        (2, True),  # Simulate an error in one of the chunks
    ],
)
# Updated patch paths based on where `sas_reader` accesses these functions
@patch("read_sas.src._sas_reader._read_file", autospec=True)
@patch("read_sas.src._sas_reader._format_filepath", autospec=True)
@patch("read_sas.src._sas_reader.n_rows_in_sas7bdat", autospec=True)
@patch("read_sas.src._sas_reader.n_gb_in_file", autospec=True)
@patch("read_sas.src._sas_reader._calculate_chunk_size", autospec=True)
def test_sas_reader(
    mock_calculate_chunk_size,
    mock_n_gb_in_file,
    mock_n_rows_in_sas7bdat,
    mock_format_filepath,
    mock_read_file,
    mock_formatter,
    mock_config,
    lazyframe,
    num_chunks,
    should_raise,
):
    """Test `sas_reader` function with different scenarios.

    Test cases include:
    - Successful processing of chunks.
    - Handling of chunk errors.
    """
    # Set up the mock return values for each function
    mock_format_filepath.return_value = Path("tinycopy.sas7bdat")
    mock_n_rows_in_sas7bdat.return_value = 1000  # Mock number of rows
    mock_n_gb_in_file.return_value = 1.0  # Mock file size in GB
    mock_calculate_chunk_size.return_value = 250  # Mock chunk size

    # Mock the `_read_file` generator to yield specific chunks
    if should_raise:
        # Simulate one chunk raising an exception
        mock_read_file.return_value = [
            (0, lazyframe),
            (1, lazyframe),
            (2, lazyframe),  # This chunk will raise an exception
        ]
        # Mock the collect method to raise an exception for the third chunk
    else:
        # No errors in chunks, so the collect method does not raise any exceptions
        mock_read_file.return_value = [(i, lazyframe) for i in range(num_chunks)]

    # Call the function under test
    result = sas_reader(
        filepath="tinycopy.sas7bdat",
        config=mock_config,
        formatter=mock_formatter,
        column_list=["col1", "col2"],
    )

    # Assertions on the concatenated result
    assert isinstance(result, pl.LazyFrame), f"Expected LazyFrame, got {type(result)}"

    # Check logger interactions
    if should_raise:
        pass
    else:
        # Ensure no errors were logged
        assert (
            mock_config.logger.debug.call_count >= num_chunks
        ), f"Expected {num_chunks} debug calls, got {mock_config.logger.debug.call_count}"
