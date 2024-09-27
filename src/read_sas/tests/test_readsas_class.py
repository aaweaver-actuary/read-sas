import pytest
from unittest.mock import Mock, patch
import polars as pl
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal
from pathlib import Path
from read_sas import ReadSas, Config


@pytest.fixture
def mock_config():
    """Fixture to create a mock Config object."""
    mock = Mock(spec=Config)
    mock.logger = Mock()
    mock.temp_dir_parent = Path("/home/andy/dev/read-sas")  # Mock the temp directory
    return mock


@pytest.fixture
def mock_formatter():
    """Fixture to create a mock formatter function."""
    return Mock(side_effect=lambda df: df)  # Return input df unchanged


@pytest.fixture
def lazyframe():
    """Fixture to create a mock polars LazyFrame."""
    df = pd.DataFrame(
        {
            "col1": np.random.default_rng(42).integers(0, 100, 1_000_000),
            "col2": np.random.default_rng(42).normal(0, 1, 1_000_000),
        }
    )

    # Write the DataFrame to Parquet
    pl.from_pandas(df).write_parquet("temp__tinycopy/tinycopy.parquet")
    return pl.from_pandas(df).lazy()


@pytest.fixture
def mock_dataframe():
    """Fixture to create a mock polars DataFrame."""
    return pl.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]}).write_parquet(
        "temp__tinycopy/tinycopy.parquet"
    )


@patch("read_sas.src._format_filepath", autospec=True)
@patch("read_sas.src.sas_reader", autospec=True)
def test_read_sas_init(mock_sas_reader, mock_format_filepath, mock_formatter):
    """Test the initialization of the ReadSas class."""
    mock_format_filepath.return_value = Path("tinycopy.sas7bdat")
    mock_sas_reader.return_value = Mock(spec=pl.LazyFrame)

    reader = ReadSas(
        "tinycopy.sas7bdat",
        formatter=mock_formatter,
        config_kwargs={"temp_dir_parent": Path("/home/andy/dev/read-sas")},
    )

    assert reader.filename == Path("tinycopy.sas7bdat")
    assert isinstance(reader.config, Config)
    assert reader.formatter == mock_formatter


@patch("read_sas.src.was_file_created_in_last_week", autospec=True)
@patch("read_sas.src._format_filepath", autospec=True)
@patch("read_sas.src.sas_reader", autospec=True)
@patch("polars.read_parquet", autospec=True)
@patch("polars.LazyFrame.collect", autospec=True)
def test_read_sas_run_no_existing_parquet(
    mock_collect,
    mock_read_parquet,
    mock_sas_reader,
    mock_format_filepath,
    mock_was_file_created,
    mock_formatter,
    lazyframe,
):
    """Test `run()` when no recent Parquet file exists."""
    mock_format_filepath.return_value = Path("tinycopy.sas7bdat")
    mock_sas_reader.return_value = lazyframe
    mock_was_file_created.return_value = False  # No recent file
    mock_collect.return_value = lazyframe
    mock_read_parquet.return_value = pl.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )

    reader = ReadSas(
        "tinycopy.sas7bdat",
        formatter=mock_formatter,
        config_kwargs={"temp_dir_parent": Path("/home/andy/dev/read-sas")},
    )
    result = reader.run()

    assert result.shape == (3, 2)
