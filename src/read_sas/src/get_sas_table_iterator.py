from pathlib import Path
import pandas as pd
from read_sas.src._format_filepath import _format_filepath
from read_sas.src.config import Config
from read_sas.src._calculate_chunk_size import _calculate_chunk_size
from read_sas.src.n_gb_in_file import n_gb_in_file
from read_sas.src.n_rows_in_sas7bdat import n_rows_in_sas7bdat
from read_sas.src.timer import timer


@timer
def get_sas_table_iterator(
    filepath: str | Path, config: Config, column_list: list[str] | str | None = None
) -> pd.io.sas.SAS7BDATReader:
    """Return an iterator to read a SAS file in chunks."""
    formatted_filepath = _format_filepath(filepath)
    return pd.read_sas(
        formatted_filepath,
        encoding="latin-1",
        chunksize=_calculate_chunk_size(
            config,
            n_rows_in_sas7bdat(formatted_filepath, column_list),
            n_gb_in_file(formatted_filepath),
            config.chunk_size_in_gb,
        ),
    )
