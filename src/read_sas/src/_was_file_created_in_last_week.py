"""Check to see if a file was created in the last week. If not, will re-pull the data."""

from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path


def was_file_created_in_last_week(filepath: str | Path) -> bool:
    """Check to see if a file was created in the last week."""
    if isinstance(filepath, str):
        filepath = Path(filepath)
    return datetime.now() - timedelta(days=7) < datetime.fromtimestamp(
        filepath.stat().st_ctime
    )
