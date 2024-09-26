from pathlib import Path
from read_sas.src._config import Config


def _format_filepath(filepath: str | Path, config: Config) -> Path:
    """Private helper function to ensure filepath is a Path object."""
    if isinstance(filepath, str):
        return Path(filepath)
    elif isinstance(filepath, Path):
        return filepath
    else:
        config.logger.error(
            f"Expected either a `str` or a `pathlib.Path` object for `filepath`, got: {type(filepath)}"
        )
        raise ValueError
