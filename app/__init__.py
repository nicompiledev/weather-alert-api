"""
Application factory module.

This module provides functions for creating and configuring the Flask
application.
"""

import os
import sqlite3
from flask import Flask
from dotenv import load_dotenv
from config.logging_config import setup_logging

# Load environment variables from .env file
load_dotenv()


def create_app():
    """
    Create and configure the Flask application.

    This function creates a new Flask application instance, configures
    logging, sets up the SQLite database, and registers blueprints.

    :return: The configured Flask application instance
    """
    app = Flask(__name__)

    # Configure logging for the application
    setup_logging()

    # Configure SQLite database (in-memory for testing)
    app.config["DATABASE"] = ":memory:"

    # Import and register blueprints for alert and notification routes
    from .routes.alert import alert_bp
    from .routes.notifications import notifications_bp

    app.register_blueprint(alert_bp, url_prefix="/alert")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")

    return app


def init_db():
    """
    Initialize the SQLite database.

    This function creates and connects to an in-memory SQLite database,
    creates the necessary tables, and commits the changes.

    :return: None
    """
    # Create and connect to the in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create the notifications table (adjust according to your needs)
    cursor.execute(
        """
    CREATE TABLE notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        location TEXT NOT NULL,
        forecast TEXT NOT NULL
    )
    """
    )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
