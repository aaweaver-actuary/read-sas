from __future__ import annotations
from read_sas.src.__format_filepath import _format_filepath
from pathlib import Path
import pyreadstat
from read_sas.src._timer import timer
from read_sas.src._config import Config


@timer
def n_rows_in_sas7bdat(
    filepath: str | Path, config: Config, column_list: list[str] | None = None
) -> int:
    """Return the number of rows in a SAS file."""
    _, meta = pyreadstat.read_sas7bdat(
        _format_filepath(filepath, config),
        disable_datetime_conversion=True,
        usecols=column_list,
        metadataonly=True,
    )

    return meta.number_rows
