from read_sas.src._format_filepath import _format_filepath
from pathlib import Path
import pyreadstat
from read_sas.src.timer import timer


@timer
def n_rows_in_sas7bdat(
    filepath: str | Path, column_list: list[str] | None = None
) -> int:
    """Return the number of rows in a SAS file."""
    _, meta = pyreadstat.read_sas7bdat(
        _format_filepath(filepath),
        disable_datetime_conversion=True,
        usecols=column_list,
        metadataonly=True,
    )

    return meta.number_rows
