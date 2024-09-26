from read_sas.src._config import Config


def _calculate_chunk_size(
    config: Config,
    n_rows_in_file: int,
    file_size_in_gb: float,
    chunk_size_in_gb: float | None = None,
) -> int:
    """Private helper function to calculate the chunk size."""
    if file_size_in_gb <= 0:
        raise ValueError(f"File size must be a positive number. Got {file_size_in_gb}.")

    if chunk_size_in_gb is not None and chunk_size_in_gb <= 0:
        raise ValueError(
            f"Chunk size must be a positive number. Got {chunk_size_in_gb}."
        )

    if n_rows_in_file <= 0:
        raise ValueError(
            f"Number of rows in file must be a positive number. Got {n_rows_in_file}."
        )

    return int(
        (n_rows_in_file / file_size_in_gb)  # num rows per Gb
        * (
            chunk_size_in_gb
            if chunk_size_in_gb is not None
            else config.chunk_size_in_gb
        )  # num rows per chunk
    )
