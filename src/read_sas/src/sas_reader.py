from __future__ import annotations
from typing import Callable, Generator
from pathlib import Path
import polars as pl
import pyreadstat
from read_sas.src.config import Config
from read_sas.src._format_filepath import _format_filepath
from read_sas.src.n_rows_in_sas7bdat import n_rows_in_sas7bdat
from read_sas.src.n_gb_in_file import n_gb_in_file
from read_sas.src._calculate_chunk_size import _calculate_chunk_size
from multiprocessing import cpu_count
from read_sas.src.timer import timer


@timer
def sas_reader(
    filepath: str | Path,
    config: Config,
    formatter: Callable[[pl.LazyFrame], pl.LazyFrame],
    column_list: list[str] | str | None = None,
) -> pl.LazyFrame:
    """Read a SAS file in chunks and apply a formatter function to each chunk."""
    filepath = _format_filepath(filepath, config)
    n_rows_in_file = n_rows_in_sas7bdat(filepath, column_list)
    file_size_in_gb = n_gb_in_file(filepath)
    chunk_size = _calculate_chunk_size(config, n_rows_in_file, file_size_in_gb)

    @timer
    def read_file() -> Generator[tuple[int, pl.DataFrame], None, None]:
        reader = pyreadstat.read_file_in_chunks(
            pyreadstat.read_sas7bdat,
            filepath,
            chunksize=chunk_size,
            usecols=column_list,
            disable_datetime_conversion=config.disable_datetime_conversion,
            multiprocess=config.use_multiprocessing,
            num_processes=config.num_processes or cpu_count(),
        )

        counter = 0
        for df, _ in reader:
            counter += 1
            yield counter, formatter(pl.from_pandas(df).lazy())

    config.logger.info(f"Number of chunks to process: {n_rows_in_file // chunk_size}")
    frames = []
    for i, lf in read_file():
        try:
            frames.append(lf.collect())
            config.logger.debug(f"Able to process chunk: {i}")
        except Exception as _:
            config.logger.debug(
                f"Was not able to process chunk: {i}. Searching for column errors."
            )
            for col in lf.columns:
                try:
                    lf.select(col).collect()
                    config.logger.debug(f"Able to process column: {col}")
                except Exception as e:
                    config.logger.error(f"Error collecting column: {col} -- {e}")
                    continue

    config.logger.debug(f"Number of chunks processed: {len(frames)}")
    config.logger.info("All chunks processed. Concatenating frames.")

    return pl.concat(frames, how="vertical")
