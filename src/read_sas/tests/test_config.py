"""Test suite for the Config dataclass.

@dataclass
class Config:
    capture_timing_stats: bool = False
    use_profiler: bool = False
    temp_dir_parent = Path("/sas/data/project/EG/ActShared/SmallBusiness/Modeling/dat")
    chunk_size_in_gb: int = 15
    logger: logging.Logger = logger
    disable_datetime_conversion: bool = True
    use_multiprocessing: bool = True
    num_processes: int | None = None

    def __post_init__(self):
        self.profiler = Profiler()
"""

from __future__ import annotations
from read_sas.src._config import Config
import pytest
from pathlib import Path
import logging


@pytest.fixture
def config() -> Config:
    """Return a Config object with default values."""
    return Config()


def test_default_values(config: Config):
    """Test the default values of the Config dataclass."""
    assert (
        config.capture_timing_stats is False
    ), f"Expected: False, Got: {config.capture_timing_stats}"
    assert config.use_profiler is False, f"Expected: False, Got: {config.use_profiler}"
    assert (
        config.temp_dir_parent
        == Path("/sas/data/project/EG/ActShared/SmallBusiness/Modeling/dat")
    ), f"Expected: /sas/data/project/EG/ActShared/SmallBusiness/Modeling/dat, Got: {config.temp_dir_parent}"
    assert (
        config.chunk_size_in_gb == 15
    ), f"Expected: 15, Got: {config.chunk_size_in_gb}"
    assert isinstance(
        config.logger, logging.Logger
    ), f"Expected: logging.Logger, Got: {type(config.logger)}"
    assert (
        config.disable_datetime_conversion
    ), f"Expected: True, Got: {config.disable_datetime_conversion}"
    assert (
        config.use_multiprocessing
    ), f"Expected: True, Got: {config.use_multiprocessing}"
    assert config.num_processes is None, f"Expected: None, Got: {config.num_processes}"


def test_custom_values():
    """Test the Config dataclass with custom values."""
    custom_logger = logging.getLogger("custom_logger")
    config = Config(
        capture_timing_stats=True,
        use_profiler=True,
        temp_dir_parent=Path("/custom/path"),
        chunk_size_in_gb=10,
        logger=custom_logger,
        disable_datetime_conversion=False,
        use_multiprocessing=False,
        num_processes=4,
    )
    assert (
        config.capture_timing_stats
    ), f"Expected: True, Got: {config.capture_timing_stats}"
    assert config.use_profiler, f"Expected: True, Got: {config.use_profiler}"
    assert config.temp_dir_parent == Path(
        "/custom/path"
    ), f"Expected: /custom/path, Got: {config.temp_dir_parent}"
    assert (
        config.chunk_size_in_gb == 10
    ), f"Expected: 10, Got: {config.chunk_size_in_gb}"
    assert (
        config.logger == custom_logger
    ), f"Expected: custom_logger, Got: {config.logger}"
    assert (
        config.disable_datetime_conversion is False
    ), f"Expected: False, Got: {config.disable_datetime_conversion}"
    assert (
        config.use_multiprocessing is False
    ), f"Expected: False, Got: {config.use_multiprocessing}"
    assert config.num_processes == 4, f"Expected: 4, Got: {config.num_processes}"
