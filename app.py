"""
This module implements a Flask web application that provides a weather alert service.

The service fetches weather forecasts for a given location using the WeatherAPI,
and sends an email notification if adverse weather conditions are predicted that
might delay package deliveries.
"""

import os
import smtplib
import sqlite3
from datetime import datetime
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError   


# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)

# Retrieve API key and email credentials from environment variables
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
EMAIL_HOST = "smtp.gmail.com"  # Gmail SMTP server
EMAIL_PORT = 587  # Port for Gmail SMTP
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


# Database setup
def init_db():
    """
    Initialize the database by creating a table for notifications if it does not exist.

    Args:
        None

    Returns:
        None

    Creates a table named 'notifications' with the following columns:
    - id (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier for each notification
    - email (TEXT NOT NULL): Email address of the recipient
    - location (TEXT NOT NULL): Location for which the forecast was made
    - forecast (TEXT NOT NULL): Weather forecast
    - sent_at (DATETIME NOT NULL): Timestamp when the notification was sent
    """
    try:
        conn = sqlite3.connect("notifications.db")
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")


init_db()

def get_weather(location):
    """
    Fetches the weather forecast for a given location.

    Args:
        location (str): The location to get the weather forecast for.
                        This can be a city name or coordinates in "latitude,longitude" format.

    Returns:
        dict: The weather forecast data in JSON format.
    """
    try:
        url = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days=2&aqi=no&alerts=no&lang=es"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def send_email(to_email, subject, body):
    """
    Sends an email with the specified subject and body.

    Args:
        to_email (str): Recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.
    """
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()  # Start TLS encryption
            server.login(EMAIL_USER, EMAIL_PASS)  # Login to the SMTP server
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(
                EMAIL_USER, to_email, message.encode("utf-8")
            )  # Send the email
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")


def save_notification(email, location, forecast):
    """
    Saves the notification details to the database.

    Args:
        email (str): Recipient's email address.
        location (str): The location for which the forecast was made.
        forecast (str): The weather forecast.
    """
    try:
        conn = sqlite3.connect("notifications.db")
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO notifications (email, location, forecast, sent_at)
        VALUES (?, ?, ?, ?)
        """,
            (email, location, forecast, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error saving notification: {e}")


@app.route("/alert", methods=["POST"])
def alert():
    """
    Endpoint to handle POST requests for weather alerts.

    Expects JSON input with 'email' and 'location' fields.
    Checks the weather forecast and sends an email if necessary.

    Returns:
        JSON: Contains the weather forecast code, description, and whether the buyer was notified.
    """
    try:
        data = request.json
        email = data["email"]
        location = data["location"]
        
        # Validate email address
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({"error": "Invalid email address"}), 400
        
        # Get the weather forecast for the provided location
        weather = get_weather(location)
        if weather is None:
            return jsonify({"error": "Failed to fetch weather data"}), 500

        forecast = weather["forecast"]["forecastday"][0]["day"]

        weather_condition = forecast["condition"]["text"]
        forecast_code = forecast["condition"]["code"]

        notify_buyer = False

        # Check if the weather condition code indicates unfavorable conditions for delivery
        if forecast_code in [1186, 1189, 1192, 1195, 1063]:
            notify_buyer = True
            email_body = (
                f"Hola! Tenemos programada la entrega de tu paquete para mañana "
                f"en la dirección de entrega, esperamos un día con {weather_condition}, "
                f"y por esta razón es posible que tengamos retrasos. "
                f"\n\nHaremos todo a nuestro alcance para cumplir con tu entrega."
            )
            send_email(
                email,
                "ENTREGA RETRASADA POR CONDICIONES CLIMÁTICAS",
                email_body,
            )

            # Save the notification to the database
            save_notification(email, location, weather_condition)

        # Return the weather forecast code, description, and notification status
        return jsonify(
            {
                "forecast_code": forecast_code,
                "forecast_description": weather_condition,
                "buyer_notification": notify_buyer,
            }
        )
    except Exception as e:
        print(f"Error processing alert: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/notifications", methods=["GET"])
def get_notifications():
    """
    Endpoint to retrieve past notifications for a given email address.

    Expects 'email' as a query parameter.

    Returns:
        JSON: Contains a list of past notifications with their details.
    """
    try:
        email = request.args.get("email")
        if not email:
            return jsonify({"error": "Email parameter is required"}), 400

        conn = sqlite3.connect("notifications.db")
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT location, forecast, sent_at FROM notifications
        WHERE email = ?
        ORDER BY sent_at DESC
        """,
            (email,),
        )
        notifications = cursor.fetchall()
        conn.close()

        return jsonify(
            {
                "notifications": [
                    {"location": n[0], "forecast": n[1], "sent_at": n[2]}
                    for n in notifications
                ]
            }
        )
    except sqlite3.Error as e:
        print(f"Error fetching notifications: {e}")
        return jsonify({"error": "Failed to fetch notifications"}), 500
    except Exception as e:
        print(f"Error processing notifications: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
