"""Logging configuration for ZK Documentation MCP Server."""

import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging():
    """Set up logging with file and console handlers.

    Configuration:
    - Log directory: ~/.zk-doc-mcp/logs/
    - Log filename pattern: zk-doc-mcp.YYYY-MM-DD.log
    - Daily rotation at midnight
    - 7 days of log retention
    - Console output: INFO level and above
    - File output: Configured level (via ZK_DOC_LOG_LEVEL env var)
    """
    # Get log level from environment variable
    log_level_str = os.getenv("ZK_DOC_LOG_LEVEL", "INFO").upper()
    try:
        log_level = getattr(logging, log_level_str)
    except AttributeError:
        log_level = logging.INFO
        print(f"Warning: Invalid ZK_DOC_LOG_LEVEL '{log_level_str}', using INFO")

    # Create logger
    logger = logging.getLogger("zk_doc_mcp")
    logger.setLevel(logging.DEBUG)  # Logger accepts all levels, handlers filter

    # Remove existing handlers (if logging was already configured)
    logger.handlers.clear()

    # Create log directory
    log_dir = Path.home() / ".zk-doc-mcp" / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Warning: Cannot create log directory {log_dir}")
        return logger
    except Exception as e:
        print(f"Warning: Error creating log directory {log_dir}: {e}")
        return logger

    # Log format
    log_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler with daily rotation
    log_file = log_dir / "zk-doc-mcp.log"
    try:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            interval=1,
            backupCount=6,
            utc=False
        )
        # Set the filename format for rotated files (YYYY-MM-DD)
        file_handler.namer = _namer
        file_handler.setLevel(log_level)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Cannot set up file logging: {e}")

    # Console handler (INFO and above, not DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    return logger


def _namer(name: str) -> str:
    """Generate rotated log filename with date.

    Convert default rotation naming to date-based format:
    Before rotation: zk-doc-mcp.log (current day's logs)
    After rotation:  zk-doc-mcp.YYYY-MM-DD.log (renamed with yesterday's date)

    Args:
        name: Original filename with potential numeric suffix

    Returns:
        Formatted filename with date in YYYY-MM-DD format
    """
    from datetime import datetime, timedelta

    # Get yesterday's date (since rotation happens at midnight)
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")

    # Return new format: zk-doc-mcp.YYYY-MM-DD.log
    parent = Path(name).parent
    return str(parent / f"zk-doc-mcp.{date_str}.log")


# Get logger instance
logger = logging.getLogger("zk_doc_mcp")
