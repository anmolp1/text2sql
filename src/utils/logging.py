

#!/usr/bin/env python3
"""
src/utils/logging.py

Initializes structured logging using structlog if available,
otherwise falls back to standard Python logging based on YAML config.
"""

import os
import logging
import logging.config
import yaml

# Attempt to import structlog for structured JSON logging
try:
    import structlog
except ImportError:
    structlog = None

def setup_logging(
    config_path: str = None,
    default_level: str = "INFO"
):
    """
    Configure logging from a YAML file.
    If structlog is installed, also configure structlog for JSON output.
    """
    # Determine config file path
    cfg_path = config_path or os.getenv("LOGGING_CONFIG_PATH", "config/logging.yaml")
    if not os.path.exists(cfg_path):
        logging.basicConfig(level=default_level)
        logging.getLogger(__name__).warning(f"Logging config file not found: {cfg_path}. Using basicConfig.")
        return

    # Load YAML config
    with open(cfg_path, "r") as f:
        config_dict = yaml.safe_load(f)

    # Apply stdlib logging config
    logging.config.dictConfig(config_dict)

    # If structlog is present, configure it to wrap stdlib
    if structlog:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="ISO"),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

# Initialize logging upon import
setup_logging()

def get_logger(name: str = __name__):
    """
    Retrieve a logger by name.
    Returns a structlog logger if structlog is available, else a standard logger.
    """
    if structlog:
        return structlog.get_logger(name)
    return logging.getLogger(name)