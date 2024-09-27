from __future__ import annotations
import polars as pl
import pyreadstat  # type: ignore
from read_sas.src._timer import timer
from read_sas.src._config import Config
from typing import Generator, Callable
from multiprocessing import cpu_count


@timer
def _read_file(
    filepath: str,
    chunk_size: int,
    column_list: list[str] | None,
    config: Config,
    formatter: Callable[[pl.LazyFrame], pl.LazyFrame] | None,
) -> Generator[tuple[int, pl.LazyFrame], None, None]:
    """Read a SAS file in chunks and apply a formatter function to each chunk.

    Parameters
    ----------
    filepath : str
        The path to the file to read.
    chunk_size : int
        The number of rows to read in each chunk.
    column_list : list[str] | None
        The list of columns to read from the file. If None, all columns are read.
    config : Config
        The ReadSas configuration object.
    formatter : Callable[[pl.LazyFrame], pl.LazyFrame] | None
        An optional formatting function to apply to each chunk.

    Yields
    ------
    tuple[int, pl.DataFrame]
        A tuple containing the index of the chunk and the chunk itself.
    """

    def cleaner(df: pl.LazyFrame) -> pl.LazyFrame:
        return formatter(df) if formatter is not None else df

    reader = pyreadstat.read_file_in_chunks(
        pyreadstat.read_sas7bdat,
        filepath,
        chunksize=chunk_size,
        usecols=column_list,
        disable_datetime_conversion=config.disable_datetime_conversion,
        multiprocess=config.use_multiprocessing,
        num_processes=config.num_processes or cpu_count(),
    )

    for i, (df, _) in enumerate(reader):
        yield i, cleaner(pl.from_pandas(df).lazy())
