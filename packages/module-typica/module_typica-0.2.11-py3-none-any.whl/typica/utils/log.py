import logging
import logging.config
import logging.handlers
import os
import sys
from enum import Enum
from typing import Any, Dict, List, Optional


class CustomLogLevel(int, Enum):
    """Defines custom logging levels."""

    NOTSET = 0
    DEBUG = 10
    CONNECTION = 15
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


_CUSTOM_LEVELS_REGISTERED = False


def add_custom_levels():
    """
    Idempotently adds custom log levels (SUCCESS, CONNECTION)
    and patches them onto the logging.Logger class.
    """
    global _CUSTOM_LEVELS_REGISTERED
    if _CUSTOM_LEVELS_REGISTERED:
        return

    # Add the level names
    logging.addLevelName(CustomLogLevel.SUCCESS, "SUCCESS")
    logging.addLevelName(CustomLogLevel.CONNECTION, "CONNECTION")

    # Define the methods
    def success(self, message, *args, **kws):
        if self.isEnabledFor(CustomLogLevel.SUCCESS):
            self._log(CustomLogLevel.SUCCESS, message, args, **kws)

    def connection(self, message, *args, **kws):
        if self.isEnabledFor(CustomLogLevel.CONNECTION):
            self._log(CustomLogLevel.CONNECTION, message, args, **kws)

    # Patch the methods onto the Logger class
    # We use type: ignore to suppress mypy errors about dynamic patching.
    logging.Logger.success = success  # type: ignore[attr-defined]
    logging.Logger.connection = connection  # type: ignore[attr-defined]

    _CUSTOM_LEVELS_REGISTERED = True


class ColoredTerminalFormatter(logging.Formatter):
    """
    An efficient colored log formatter.

    This formatter creates and caches a separate logging.Formatter
    instance for each log level, applying ANSI color codes.
    This avoids re-creating a Formatter object for every log record.
    """

    # ANSI color codes
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    BLUE = "\x1b[38;2;122;115;209m"
    PURPLE = "\x1b[38;2;181;168;213m"
    RESET = "\x1b[0m"

    # Mapping of log levels to colors
    LEVEL_COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREY,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
        CustomLogLevel.SUCCESS: GREEN,
        CustomLogLevel.CONNECTION: PURPLE,
    }

    def __init__(
        self,
        fmt: str = "%(levelname)-8s | %(name)s - %(message)s",
        datefmt: str = "%Y-%m-%d %H:%M:%S",
    ):
        """
        Initializes the formatter.

        :param fmt: The base log format string.
        :param datefmt: The date format string.
        """
        super().__init__(datefmt=datefmt)
        self.base_fmt = fmt
        self.datefmt = datefmt

        # Cache of formatters, one for each level
        self.formatters = {}

        # Create a default formatter for levels without a specific color
        self.default_formatter = logging.Formatter(
            self.base_fmt, datefmt=self.datefmt
        )

        # Create colored formatters
        for level, color in self.LEVEL_COLORS.items():
            # Add color and reset codes around the base format
            log_fmt = color + self.base_fmt + self.RESET
            self.formatters[level] = logging.Formatter(
                log_fmt, datefmt=self.datefmt
            )

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log record.

        This method selects the pre-compiled formatter based on the
        record's level number.
        """
        # Get the cached formatter, or use the default
        formatter = self.formatters.get(record.levelno, self.default_formatter)
        return formatter.format(record)


DEFAULT_FILE_FORMAT = "[%(levelname)-8s] %(asctime)s - %(name)s:%(filename)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_CONSOLE_FORMAT = (
    "%(levelname)-8s | %(filename)s:%(lineno)d - %(message)s"
)


def setup_logger(
    name: Optional[str] = None,
    base_level: int = CustomLogLevel.DEBUG,
    console: bool = True,
    console_level: int = CustomLogLevel.DEBUG,
    log_dir: str = "./logs",
    file_handlers_config: Optional[List[Dict[str, Any]]] = None,
) -> logging.Logger:
    """
    Programmatically sets up a logger in a reusable way.

    This function replaces the need for a static LOGCONFIG dictionary.

    :param name: The name of the logger (e.g., 'my_app', 'db_client').
                 If None, configures the root logger.
    :param base_level: The base level for the logger object (e.g., CustomLogLevel.DEBUG).
                       This is the lowest level the logger will process.
    :param console: Whether to add a colored console handler (to stdout).
    :param console_level: The minimum level for the console handler.
    :param log_dir: The base directory for all log files. Will be created if it
                    doesn't exist.
    :param file_handlers_config: A list of dicts, where each dict configures
                                 a RotatingFileHandler.
        Example:
        [
            {
                "filename": "app.log",
                "level": CustomLogLevel.CONNECTION,
                "max_bytes": 1_048_576,  # 1 MB
                "backup_count": 4
            },
            {
                "filename": "full_app.log",
                "level": CustomLogLevel.DEBUG,
                "max_bytes": 5_242_880,  # 5 MB
                "backup_count": 2
            }
        ]
    :return: The configured logging.Logger instance.
    """
    # 1. Register custom levels (this is idempotent)
    add_custom_levels()

    # 2. Get the logger and set its base level
    logger = logging.getLogger(name)
    logger.setLevel(base_level)

    # 3. Clear any existing handlers to avoid duplication
    #    This is useful for reconfiguration or in environments like notebooks.
    if logger.hasHandlers():
        logger.handlers = []

    # 4. If it's a named logger (not root), stop it from propagating
    #    logs to the root logger. This gives you isolated configs.
    if name:
        logger.propagate = False

    # 5. Create and add console handler
    if console:
        try:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(console_level)

            console_formatter = ColoredTerminalFormatter(
                fmt=DEFAULT_CONSOLE_FORMAT, datefmt=DEFAULT_DATE_FORMAT
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        except Exception as e:
            print(
                f"Error: Could not set up console logging. {e}", file=sys.stderr
            )

    # 6. Create and add file handlers
    if file_handlers_config:
        # Ensure log directory exists
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError as e:
                print(
                    f"Warning: Could not create log directory {log_dir}. {e}",
                    file=sys.stderr,
                )

        # Create a standard (non-colored) formatter for files
        file_formatter = logging.Formatter(
            DEFAULT_FILE_FORMAT, datefmt=DEFAULT_DATE_FORMAT
        )

        for config in file_handlers_config:
            try:
                # Get required 'filename'
                filename = config["filename"]
                file_path = os.path.join(log_dir, filename)

                # Get optional params with sensible defaults
                file_level = config.get("level", CustomLogLevel.INFO)
                max_bytes = config.get("max_bytes", 1_048_576)  # 1 MB
                backup_count = config.get("backup_count", 3)

                # Create the handler
                file_handler = logging.handlers.RotatingFileHandler(
                    file_path,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8",  # Good practice
                )
                file_handler.setLevel(file_level)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

            except KeyError:
                print(
                    f"Warning: Skipping file handler. Config missing 'filename': {config}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"Warning: Could not create file handler for {config.get('filename')}. {e}",
                    file=sys.stderr,
                )

    return logger


# --- Preset 1: Basic Console Logging ---
# Simple, high-level logging to the console. Good for simple scripts.
PRESET_BASIC_CONSOLE = {
    "name": "basic_app",
    "base_level": CustomLogLevel.INFO,
    "console": True,
    "console_level": CustomLogLevel.INFO,
    "file_handlers_config": None,  # No files
}

# --- Preset 2: Replicates Original Config ---
# This is the config from your original request:
# - Console: DEBUG
# - "app.log": CONNECTION level, 1MB, 4 backups
# - "full_app.log": DEBUG level, 5MB, 2 backups
PRESET_ORIGINAL_FULL = {
    "name": None,  # Configures the root logger
    "base_level": CustomLogLevel.DEBUG,
    "console": True,
    "console_level": CustomLogLevel.DEBUG,
    "log_dir": "./logs_preset_original",
    "file_handlers_config": [
        {
            "filename": "app.log",
            "level": CustomLogLevel.CONNECTION,
            "max_bytes": 1048576,
            "backup_count": 4,
        },
        {
            "filename": "full_app.log",
            "level": CustomLogLevel.DEBUG,
            "max_bytes": 5242880,
            "backup_count": 2,
        },
    ],
}

# --- Preset 3: Production Setup ---
# A common setup for a production application:
# - Console: INFO level (to keep stdout clean)
# - File: DEBUG level (to capture all details for debugging)
PRESET_PRODUCTION = {
    "name": "prod_app",
    "base_level": CustomLogLevel.DEBUG,  # Logger must be DEBUG to send to file
    "console": True,
    "console_level": CustomLogLevel.INFO,  # But console only shows INFO+
    "log_dir": "./logs_preset_prod",
    "file_handlers_config": [
        {
            "filename": "prod_debug.log",
            "level": CustomLogLevel.DEBUG,  # Catches everything
            "max_bytes": 10_000_000,  # 10MB
            "backup_count": 5,
        }
    ],
}

# --- Preset 4: Isolated Module Logger ---
# A separate logger for a specific part of your app, e.g., a database module.
# This will log to its own file and not print to console.
PRESET_DB_MODULE = {
    "name": "database",  # Named logger
    "base_level": CustomLogLevel.DEBUG,
    "console": False,  # No console output from this module
    "log_dir": "./logs_preset_db",
    "file_handlers_config": [
        {
            "filename": "db_queries.log",
            "level": CustomLogLevel.CONNECTION,  # Only log connections and higher
            "max_bytes": 2_000_000,
            "backup_count": 2,
        }
    ],
}
