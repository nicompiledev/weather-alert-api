"""
Logging configuration module.

This module provides a function for setting up the global logger.
"""

import logging
import os


def setup_logging():
    """
    Set up the global logger.

    This function determines the logging level based on the environment
    and configures the global logger accordingly.

    :return: None
    """
    # Determine the logging level according to the environment
    env = os.getenv("FLASK_ENV", "development")
    # Default to development environment if FLASK_ENV is not set

    # Set the logging level based on the environment
    if env == "production":
        # In production, log only warnings and errors
        level = logging.WARNING
    else:
        # In development, log more messages for debugging purposes
        level = logging.DEBUG

    # Configure the global logger
    logging.basicConfig(
        level=level,
        # Log format: timestamp, logger name, log level, log message
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
