from __future__ import annotations
from pathlib import Path
from read_sas.src._config import Config
from read_sas.src._timer import timer


@timer
def n_gb_in_file(filepath: str | Path, config: Config) -> float:
    """Return the size of the file in Gb."""
    if isinstance(filepath, str):
        return Path(filepath).stat().st_size / 1_000_000_000
    elif isinstance(filepath, Path):
        return filepath.stat().st_size / 1_000_000_000
    else:
        config.logger.error(
            f"Invalid type for filepath: {type(filepath)}, expected str or Path."
        )
        raise ValueError
