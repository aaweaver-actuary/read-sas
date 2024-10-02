from __future__ import annotations
import time
from typing import Callable
from read_sas.src import Config, timer, sas_reader, _format_filepath
import pandas as pd
import polars as pl
from pathlib import Path


class ReadSas:
    """Encapsulate the process of reading a SAS file."""

    def __init__(
        self,
        filename: str | Path,
        formatter: Callable[[pl.LazyFrame], pl.LazyFrame] | None = None,
        column_list: list[str] | str | None = None,
        config_kwargs: dict | None = None,
    ) -> None:
        self._filename = _format_filepath(filename)
        self._config = Config(**(config_kwargs or {}))
        self._formatter = formatter
        self._column_list = column_list

        start = time.time()
        self._config.logger.info(
            f"Started reading the file: {self._filename} at {start}."
        )
        self._reader: pl.LazyFrame = sas_reader(
            self._filename, self._config, self._formatter, self._column_list
        )
        end = time.time()
        self._config.logger.info(
            f"Finished reading the file: {self._filename} at {end}."
        )
        self._config.logger.info(f"Time taken to read the file: {end - start} seconds.")

    @property
    def filename(self) -> Path:
        return self._filename

    @property
    def config(self) -> Config:
        return self._config

    @property
    def reader(self) -> pl.LazyFrame:
        return self._reader

    @property
    def column_list(self) -> list[str] | str | None:
        """Return the list of columns to read from the file."""
        return self._column_list

    @property
    def formatter(self) -> Callable[[pl.LazyFrame], pl.LazyFrame] | None:
        """Return the formatter function."""
        return self._formatter if self._formatter is not None else (lambda df: df)

    @timer
    def run(self) -> pd.DataFrame:
        """Run the reader and return the collected DataFrame."""
        filename = self.filename.stem
        folder = self.config.temp_dir_parent / f"temp__{filename}"
        folder.mkdir(parents=True, exist_ok=True)

        start = time.time()
        self.config.logger.info(
            f"Collecting the DataFrame from the reader started at {start}."
        )
        df = self.reader.collect()
        end = time.time()
        self.config.logger.info(
            f"Collecting the DataFrame from the reader finished at {end}."
        )
        self.config.logger.info(
            f"Time taken to collect the DataFrame: {end - start} seconds."
        )

        start = time.time()
        self.config.logger.info(
            f"Writing the DataFrame to a parquet file started at {start}."
        )
        df.write_parquet(folder / f"{filename}.parquet")
        end = time.time()
        self.config.logger.info(
            f"Writing the DataFrame to a parquet file finished at {end}."
        )
        self.config.logger.info(
            f"Time taken to write the DataFrame to a parquet file: {end - start} seconds."
        )

        try:
            self.config.logger.info(
                "Trying to convert the DataFrame to pandas to return."
            )
            return df.to_pandas()
        except Exception as e1:
            self.config.logger.error(
                f"Failed to convert the DataFrame to pandas. Error: {e1}."
            )
            try:
                return pl.read_parquet(folder / f"{filename}.parquet").to_pandas()
            except Exception as e:
                self.config.logger.error(
                    f"Failed to read the parquet file. Error: {e}."
                )
                raise e
