import sys
from pathlib import Path

from loguru import logger

_LOG_DIR = Path.home() / ".universal_mcp" / "logs"

_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "{name}:{function}:{line} - {message}"
)
_STDERR_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

_initialized = False


def setup_logger(
    stderr_level: str = "INFO",
    file_level: str = "DEBUG",
    rotation: str = "10 MB",
    retention: str = "1 week",
    compression: str = "zip",
) -> Path:
    """Setup the logger with stderr + file sinks.

    stderr: shows ``stderr_level`` and above (default INFO).
    File:   captures everything from ``file_level`` (default DEBUG) with
            rotation, retention and compression.

    The log file lives at ``~/.universal_mcp/logs/universal_mcp.log``
    and rotates at *rotation* size, keeping *retention* worth of history.

    Returns:
        Path to the active log file.
    """
    global _initialized
    if _initialized:
        return _log_file_path()

    # Remove default handler
    logger.remove()

    # stderr – human-friendly, configurable level
    logger.add(
        sink=sys.stderr,
        level=stderr_level,
        format=_STDERR_FORMAT,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # File – always DEBUG, machine-parseable
    log_file = _log_file_path()
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        sink=str(log_file),
        level=file_level,
        format=_FILE_FORMAT,
        rotation=rotation,
        retention=retention,
        compression=compression,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    _initialized = True
    logger.debug(f"File logging initialised → {log_file}")
    return log_file


def _log_file_path() -> Path:
    return _LOG_DIR / "universal_mcp.log"


def get_log_file_path(app_name: str = "universal-mcp") -> Path:
    """Get log file path (backward compat)."""
    return _log_file_path()
