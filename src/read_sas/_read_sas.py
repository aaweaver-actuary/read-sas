from typing import Callable
from read_sas.src import (
    Config,
    _timer,
    sas_reader,
    _format_filepath,
    Profiler,
    was_file_created_in_last_week,
)
import polars as pl
from pathlib import Path


class ReadSas:
    def __init__(
        self,
        filename: str | Path,
        formatter: Callable[pl.LazyFrame, pl.LazyFrame] | None = None,
        column_list: list[str] | str | None = None,
        config_kwargs: dict | None = None,
    ) -> None:
        """Main function to read a SAS file."""
        self._filename = _format_filepath(filename)
        self._config = Config(**(config_kwargs or {}))
        self._formatter = formatter
        self._column_list = column_list
        self._reader = sas_reader(
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
        return self._column_list

    @_timer
    def run(self) -> None:
        filename = self.filename.stem
        folder = self.config.temp_dir_parent / f"temp__{filename}"
        folder.mkdir(parents=True, exist_ok=True)

        if was_file_created_in_last_week(folder / f"{filename}.parquet"):
            return pl.read_parquet(folder / f"{filename}.parquet")

        self.reader.collect().write_parquet(folder / f"{filename}.parquet")
        return pl.read_parquet(folder / f"{filename}.parquet")
