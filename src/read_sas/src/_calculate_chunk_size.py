from read_sas.src.config import Config


def _calculate_chunk_size(
    config: Config,
    n_rows_in_file: int,
    file_size_in_gb: float,
    chunk_size_in_gb: float | None = None,
) -> int:
    """Private helper function to calculate the chunk size."""
    return int(
        (n_rows_in_file / file_size_in_gb)  # num rows per Gb
        * (
            chunk_size_in_gb
            if chunk_size_in_gb is not None
            else config.chunk_size_in_gb
        )  # num rows per chunk
    )
