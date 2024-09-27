from __future__ import annotations
from pathlib import Path
from read_sas.src._timer import timer


@timer
def n_gb_in_file(filepath: str | Path) -> float:
    """Return the size of the file in Gb."""
    valid_input_types = (str, Path)
    if isinstance(filepath, str):
        return Path(filepath).stat().st_size / 1_000_000_000
    elif not isinstance(filepath, valid_input_types):
        raise ValueError(
            f"Invalid input type: expected {valid_input_types}, got {type(filepath)}"
        )

    return filepath.stat().st_size / 1_000_000_000
