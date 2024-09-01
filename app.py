"""
This module implements a Flask web application that provides a weather alert service.

The service fetches weather forecasts for a given location using the WeatherAPI,
and sends an email notification if adverse weather conditions are predicted that
might delay package deliveries.
"""

import os
import smtplib
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)

# Retrieve API key and email credentials from environment variables
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
EMAIL_HOST = "smtp.gmail.com"  # Gmail SMTP server
EMAIL_PORT = 587  # Port for Gmail SMTP
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def get_weather(location):
    """
    Fetches the weather forecast for a given location.

    Args:
        location (str): The location to get the weather forecast for.
                        This can be a city name or coordinates in "latitude,longitude" format.

    Returns:
        dict: The weather forecast data in JSON format.
    """
    url = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days=2&aqi=no&alerts=no&lang=es"
    response = requests.get(url, timeout=10)
    return response.json()


def send_email(to_email, subject, body):
    """
    Sends an email with the specified subject and body.

    Args:
        to_email (str): Recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.
    """
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()  # Start TLS encryption
        server.login(EMAIL_USER, EMAIL_PASS)  # Login to the SMTP server
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL_USER, to_email, message.encode("utf-8"))  # Send the email


@app.route("/alert", methods=["POST"])
def alert():
    """
    Endpoint to handle POST requests for weather alerts.

    Expects JSON input with 'email' and 'location' fields.
    Checks the weather forecast and sends an email if necessary.

    Returns:
        JSON: Contains the weather forecast code, description, and whether the buyer was notified.
    """
    data = request.json
    email = data["email"]
    location = data["location"]

    # Get the weather forecast for the provided location
    weather = get_weather(location)
    forecast = weather["forecast"]["forecastday"][0]["day"]

    weather_condition = forecast["condition"][
        "text"
    ]  # Description of the weather condition
    forecast_code = forecast["condition"]["code"]  # Weather condition code

    notify_buyer = False  # Flag to determine if the buyer should be notified

    # Check if the weather condition code indicates unfavorable conditions for delivery
    if forecast_code in [1186, 1189, 1192, 1195]:
        notify_buyer = True
        email_body = (
            f"Hola! Tenemos programada la entrega de tu paquete para mañana "
            f"en la dirección de entrega, esperamos un día con {weather_condition}, "
            f"y por esta razón es posible que tengamos retrasos."
            f"Haremos todo a nuestro alcance para cumplir con tu entrega."
        )
        send_email(
            email,
            "ENTREGA RETRASADA POR CONDICIONES CLIMÁTICAS",
            email_body,
        )

    # Return the weather forecast code, description, and notification status
    return jsonify(
        {
            "forecast_code": forecast_code,
            "forecast_description": weather_condition,
            "buyer_notification": notify_buyer,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
