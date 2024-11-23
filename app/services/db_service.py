"""
Database module for storing and retrieving notifications.

This module provides functions for initializing the database, saving
notifications, and retrieving notifications by email.
"""

import sqlite3
from datetime import datetime

# Name of the database file
DB_NAME = "notifications.db"


def init_db():
    """
    Initialize the database by creating the notifications table.

    This function creates the notifications table if it does not already
    exist. The table has the following columns:
    - id (primary key, auto-incrementing integer)
    - email (text, not null)
    - location (text, not null)
    - forecast (text, not null)
    - sent_at (datetime, not null)

    :return: None
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Create the notifications table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                location TEXT NOT NULL,
                forecast TEXT NOT NULL,
                sent_at DATETIME NOT NULL
            )
            """
        )

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        # Print any errors that occur
        print(f"Error initializing database: {e}")


def save_notification(email, location, forecast):
    """
    Save a notification to the database.

    This function inserts a new row into the notifications table with the
    provided email, location, and forecast.

    :param email: The email address associated with the notification
    :param location: The location associated with the notification
    :param forecast: The forecast associated with the notification
    :return: None
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Insert the notification into the database
        cursor.execute(
            """
            INSERT INTO notifications (email, location, forecast, sent_at)
            VALUES (?, ?, ?, ?)
            """,
            (email, location, forecast, datetime.now().isoformat()),
        )

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        # Print any errors that occur
        print(f"Error saving notification: {e}")


def get_notifications_by_email(email):
    """
    Retrieve a list of notifications for a given email address.

    This function queries the notifications table for rows where the email
    address matches the provided email. The results are returned as a list
    of dictionaries, where each dictionary represents a notification.

    :param email: The email address for which to retrieve notifications
    :return: A list of notifications for the given email address
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Query the notifications table for rows matching the email address
        cursor.execute(
            """
            SELECT location, forecast, sent_at FROM notifications
            WHERE email = ?
            ORDER BY sent_at DESC
            """,
            (email,),
        )

        # Fetch the results and close the connection
        notifications = cursor.fetchall()
        conn.close()

        # Convert the results to a list of dictionaries
        return [
            {"location": n[0], "forecast": n[1], "sent_at": n[2]} for n in notifications
        ]
    except sqlite3.Error as e:
        # Print any errors that occur and return an empty list
        print(f"Error fetching notifications: {e}")
        return []
