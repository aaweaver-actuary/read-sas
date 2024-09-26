from read_sas.src import (
    Config,
    n_gb_in_file,
    n_rows_in_sas7bdat,
    sas_reader,
)
from functools import partial

partial_reader = partial(sas_reader, Config)


def main(config_kwargs: dict | None = None) -> None:
    """Main function to read a SAS file."""
    config = Config(**(config_kwargs or {}))
    reader = sas_reader(config)