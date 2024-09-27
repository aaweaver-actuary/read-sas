from __future__ import annotations
from pathlib import Path


def _format_filepath(filepath: str | Path) -> Path:
    """Private helper function to ensure filepath is a Path object."""
    valid_input_types = (str, Path)
    if isinstance(filepath, str):
        return Path(filepath)
    elif not isinstance(filepath, valid_input_types):
        raise ValueError(
            f"Expected either a `str` or a `pathlib.Path` object for `filepath`, got: {type(filepath)}"
        )

    return filepath
