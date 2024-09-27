from __future__ import annotations
import pytest
from unittest.mock import Mock, patch
from multiprocessing import cpu_count
from typing import Generator, Literal
import pyreadstat  # type: ignore
import pandas as pd
from pandas.testing import assert_frame_equal
import polars as pl
from read_sas.src.__read_file import _read_file


# Mock Formatter Function
@pytest.fixture
def mock_formatter():
    """Fixture to create a mock formatter function that simply returns the input DataFrame."""
    return Mock(side_effect=lambda df: df)


@pytest.fixture
def mock_config():
    """Fixture to create a mock config object with necessary attributes."""
    mock = Mock()
    mock.disable_datetime_conversion = True
    mock.use_multiprocessing = True
    mock.num_processes = None  # Let it use the default CPU count
    return mock


@pytest.fixture
def mock_dataframe():
    """Fixture to create a mock pandas DataFrame to simulate the chunks."""
    return Mock()


@pytest.mark.parametrize(
    "chunk_size, column_list, num_chunks, chunk_content",
    [
        (
            1000,
            ["col1", "col2"],
            3,
            [  # 3 chunks with content
                {"col1": [1, 2], "col2": [3, 4]},
                {"col1": [5, 6], "col2": [7, 8]},
                {"col1": [9, 10], "col2": [11, 12]},
            ],
        ),
        (500, ["col1"], 1, [{"col1": [1, 2, 3]}]),  # 1 chunk with fewer columns
        (2000, None, 0, []),  # No chunks returned
    ],
)
@patch("pyreadstat.read_file_in_chunks")
def test__read_file(
    mock_read_file_in_chunks,
    chunk_size: Literal[500, 1000, 2000],
    column_list: list[str] | None,
    num_chunks: Literal[0, 1, 3],
    chunk_content: list[dict[str, list[int]]],
    mock_formatter: Mock,
    mock_config: Mock,
):
    """Parameterized test for the `_read_file` generator function.

    It checks that the function correctly yields the expected number of chunks and
    that the output is correctly formatted with polars.
    """
    # Create mock chunks to return
    mock_chunks = [(pd.DataFrame(content), None) for content in chunk_content]

    # Mock the reader to yield the chunks
    mock_read_file_in_chunks.return_value = (chunk for chunk in mock_chunks)

    # Call the _read_file generator and collect results
    results = list(
        _read_file(
            filepath="dummy_path.sas7bdat",
            chunk_size=chunk_size,
            column_list=column_list,
            config=mock_config,
            formatter=mock_formatter,
        )
    )

    # Check that the number of chunks yielded is as expected
    assert len(results) == num_chunks

    # Check the content of each yielded chunk
    for i, (index, df) in enumerate(results):
        assert index == i  # Check that the index is yielded correctly
        assert isinstance(df, pl.LazyFrame)  # Ensure it's a polars LazyFrame
        # Check that the dataframe content matches the mock content
        assert_frame_equal(df.collect().to_pandas(), pd.DataFrame(chunk_content[i]))

    # Check that the formatter was called correctly
    assert mock_formatter.call_count == num_chunks

    # Ensure the reader was called with correct parameters
    mock_read_file_in_chunks.assert_called_once_with(
        pyreadstat.read_sas7bdat,
        "dummy_path.sas7bdat",  # Replace this with the actual test filepath if necessary
        chunksize=chunk_size,
        usecols=column_list,
        disable_datetime_conversion=mock_config.disable_datetime_conversion,
        multiprocess=mock_config.use_multiprocessing,
        num_processes=mock_config.num_processes or cpu_count(),
    )


@patch("pyreadstat.read_file_in_chunks")
def test__read_file_empty_chunk(
    mock_read_file_in_chunks, mock_formatter: Mock, mock_config: Mock
):
    """Test that the `_read_file` generator handles an empty chunk correctly."""
    # Mock the reader to return no chunks
    mock_read_file_in_chunks.return_value = iter([])

    # Call the generator and collect results
    results = list(
        _read_file(
            filepath="dummy_path.sas7bdat",
            chunk_size=1000,
            column_list=["col1", "col2"],
            config=mock_config,
            formatter=mock_formatter,
        )
    )

    # Ensure no chunks are yielded
    assert len(results) == 0

    # Ensure the formatter was not called
    mock_formatter.assert_not_called()


@patch("pyreadstat.read_file_in_chunks")
def test__read_file_single_chunk(
    mock_read_file_in_chunks, mock_formatter: Mock, mock_config: Mock
):
    """Test that the `_read_file` generator correctly handles a single chunk."""
    # Mock a single chunk
    mock_chunk_content = {"col1": [1, 2], "col2": [3, 4]}
    mock_chunk = pd.DataFrame(mock_chunk_content), None
    mock_read_file_in_chunks.return_value = iter([mock_chunk])

    # Call the generator and collect results
    results = list(
        _read_file(
            filepath="dummy_path.sas7bdat",
            chunk_size=1000,
            column_list=["col1", "col2"],
            config=mock_config,
            formatter=mock_formatter,
        )
    )

    # Ensure only one chunk is yielded
    assert len(results) == 1, f"Expected: 1, Got: {len(results)}"

    # Check the yielded chunk content
    index, df = results[0]
    assert index == 0, f"Expected: 0 (first chunk), Got: {index}"
    assert isinstance(df, pl.LazyFrame), f"Expected: pl.LazyFrame, Got: {type(df)}"
    assert_frame_equal(df.collect().to_pandas(), pd.DataFrame(mock_chunk_content))

    # Ensure the formatter was called once
    mock_formatter.assert_called_once()
