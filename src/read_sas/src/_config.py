from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import logging
from read_sas.src._logger import logger


@dataclass
class Config:
    capture_timing_stats: bool = False
    use_profiler: bool = False
    temp_dir_parent: Path = Path(
        "/sas/data/project/EG/ActShared/SmallBusiness/Modeling/dat"
    )
    chunk_size_in_gb: int = 15
    logger: logging.Logger = logger
    disable_datetime_conversion: bool = True
    use_multiprocessing: bool = True
    num_processes: int | None = None
