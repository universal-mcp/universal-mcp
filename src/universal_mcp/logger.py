import sys,os
from datetime import datetime
from pathlib import Path

from loguru import logger

UNIVERSAL_MCP_HOME = os.path.join(os.path.expanduser("~"), ".universal-mcp", "logs")

def setup_logger(
    log_file: Path | None = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    compression: str = "zip",
    level: str = "INFO",
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
) -> None:
    """Setup the logger with both stderr and optional file logging with rotation.

    Args:
        log_file: Optional path to log file. If None, only stderr logging is enabled.
        rotation: When to rotate the log file. Can be size (e.g., "10 MB") or time (e.g., "1 day").
        retention: How long to keep rotated log files (e.g., "1 week").
        compression: Compression format for rotated logs ("zip", "gz", or None).
        level: Minimum logging level.
        format: Log message format string.
    """
    
    if log_file is None:
        log_file = get_log_file_path()
    # Remove default handler
    logger.remove()

    # Add stderr handler
    logger.add(
        sink=sys.stderr,
        level=level,
        format=format,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # Add file handler if log_file is specified
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            sink=str(log_file),
            rotation=rotation,
            retention=retention,
            compression=compression,
            level=level,
            format=format,
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )


def get_log_file_path(app_name: str="universal_mcp") -> Path:
    """Get a standardized log file path for an application.

    Args:
        app_name: Name of the application.

    Returns:
        Path to the log file in the format: logs/{app_name}/{app_name}_{date}.log
    """
    date_str = datetime.now().strftime("%Y%m%d")
    log_dir = Path(UNIVERSAL_MCP_HOME)
    return log_dir / f"{app_name}_{date_str}.log"
    