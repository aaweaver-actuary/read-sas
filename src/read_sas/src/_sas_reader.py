from __future__ import annotations
from typing import Callable
from pathlib import Path
import polars as pl
from read_sas.src._config import Config
from read_sas.src.__format_filepath import _format_filepath
from read_sas.src._n_rows_in_sas7bdat import n_rows_in_sas7bdat
from read_sas.src._n_gb_in_file import n_gb_in_file
from read_sas.src.__calculate_chunk_size import _calculate_chunk_size
from read_sas.src._timer import timer
from read_sas.src.__read_file import _read_file


@timer
def sas_reader(
    filepath: str | Path,
    config: Config,
    formatter: Callable[[pl.LazyFrame], pl.LazyFrame],
    column_list: list[str] | str | None = None,
) -> pl.LazyFrame:
    """Read a SAS file in chunks and apply a formatter function to each chunk."""
    filepath = _format_filepath(filepath)
    n_rows_in_file = n_rows_in_sas7bdat(filepath, column_list)
    file_size_in_gb = n_gb_in_file(filepath)
    chunk_size = _calculate_chunk_size(config, n_rows_in_file, file_size_in_gb)

    config.logger.info(f"Number of chunks to process: {n_rows_in_file // chunk_size}")
    frames: list[pl.LazyFrame] = []
    for i, lf in _read_file(filepath, chunk_size, column_list, config, formatter):
        try:
            lf.collect()  # this will raise an exception if there is an error in the chunk
            frames.append(lf)
            config.logger.debug(f"Able to process chunk: {i}")
        except Exception as _:  # noqa: PERF203
            config.logger.debug(
                f"Was not able to process chunk: {i}. Searching for column errors."
            )
            for col in lf.collect_schema().names():
                try:
                    lf.select(col).collect()
                    config.logger.debug(f"Able to process column: {col}")
                except Exception as e:  # noqa: PERF203
                    config.logger.error(f"Error collecting column: {col} -- {e}")
                    continue

    config.logger.debug(f"Number of chunks processed: {len(frames)}")
    config.logger.info("All chunks processed. Concatenating frames.")

    if (not frames) or (len(frames) == 0):
        return pl.LazyFrame()

    output: pl.LazyFrame = pl.concat(frames, how="vertical")
    config.logger.info(
        f"Frames concatenated. Returning output:\n{output.collect().head()}"
    )
    return output
