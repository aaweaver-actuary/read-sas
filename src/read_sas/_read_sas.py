from __future__ import annotations
from typing import Callable
from read_sas.src import (
    Config,
    timer,
    sas_reader,
    _format_filepath,
    was_file_created_in_last_week,
)
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
        self._reader: pl.LazyFrame = sas_reader(
            self._filename, self._config, self._formatter, self._column_list
        )

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
    def run(self) -> pl.DataFrame:
        """Run the reader and return the collected DataFrame."""
        filename = self.filename.stem
        folder = self.config.temp_dir_parent / f"temp__{filename}"
        folder.mkdir(parents=True, exist_ok=True)

        can_use_previously_created_file = was_file_created_in_last_week(
            folder / f"{filename}.parquet"
        )

        if can_use_previously_created_file:
            try:
                return pl.read_parquet(folder / f"{filename}.parquet")
            except Exception as e:
                self.config.logger.warning(
                    f"Failed to read the parquet file. Error: {e}. Reading the SAS file again."
                )

        self.reader.collect().write_parquet(folder / f"{filename}.parquet")
        try:
            return pl.read_parquet(folder / f"{filename}.parquet")
        except Exception as e:
            self.config.logger.error(f"Failed to read the parquet file. Error: {e}.")
            raise e
