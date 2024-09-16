import unittest
from unittest.mock import patch, MagicMock
import requests
import sqlite3
import smtplib
import os
from app import (
    init_db,
    get_weather,
    send_email,
    save_notification,
    app,
)


class TestWeatherAlertService(unittest.TestCase):

    def setUp(self):
        # Initialize the database before each test (in-memory for speed)
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        init_db()  # Initialize the in-memory database

    def tearDown(self):
        # Close the in-memory database
        self.conn.close()

    @patch("requests.get")
    def test_get_weather_success(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "forecast": {
                "forecastday": [{"day": {"condition": {"text": "Sunny", "code": 1000}}}]
            }
        }
        mock_get.return_value = mock_response

        # Test the function
        location = "New York"
        weather = get_weather(location)
        self.assertIsNotNone(weather)
        self.assertIn("forecast", weather)

    @patch("requests.get")
    def test_get_weather_failure(self, mock_get):
        # Mock the API request failure
        mock_get.side_effect = requests.exceptions.RequestException

        # Test the function
        location = "New York"
        weather = get_weather(location)
        self.assertIsNone(weather)

    @patch("requests.get")
    def test_get_weather_timeout(self, mock_get):
        # Mock a request timeout
        mock_get.side_effect = requests.exceptions.Timeout

        # Test the function
        location = "New York"
        weather = get_weather(location)
        self.assertIsNone(weather)

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        # Mock the SMTP connection
        mock_smtp.return_value.__enter__.return_value = mock_smtp

        # Test the function
        to_email = "test@example.com"
        subject = "Test Email"
        body = "Hello, World!"
        send_email(to_email, subject, body)

        # Assert that the email was sent successfully
        mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_email_failure(self, mock_smtp):
        # Mock the SMTP connection failure
        mock_smtp.side_effect = smtplib.SMTPException

        # Test the function
        to_email = "test@example.com"
        subject = "Test Email"
        body = "Hello, World!"

        # Capture printed error message
        with self.assertLogs(level="ERROR") as log:
            send_email(to_email, subject, body)

        # Assert that an error message was printed
        self.assertIn("Error sending email:", log.output[0])

    @patch("sqlite3.connect")
    def test_save_notification_success(self, mock_connect):
        # Mock the database connection
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Test the function
        email = "test@example.com"
        location = "New York"
        forecast = "Sunny"
        save_notification(email, location, forecast)

        # Assert that the notification was saved successfully
        mock_conn.cursor.return_value.execute.assert_called_once()

    @patch("sqlite3.connect")
    def test_save_notification_failure(self, mock_connect):
        # Mock the database connection failure
        mock_connect.side_effect = sqlite3.Error

        # Test the function
        email = "test@example.com"
        location = "New York"
        forecast = "Sunny"

        # Capture printed error message
        with self.assertLogs(level="ERROR") as log:
            save_notification(email, location, forecast)

        # Assert that an error message was printed
        self.assertIn("Error saving notification:", log.output[0])


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        # Create a test client for the Flask app
        self.app = app.test_client()
        # Set the environment variable to indicate testing
        os.environ["TESTING"] = "True"
        # Initialize the database before each test (in-memory)
        self.conn = sqlite3.connect(":memory:")
        init_db()

    def tearDown(self):
        # Close the in-memory database
        self.conn.close()
        # Reset the environment variable
        os.environ.pop("TESTING", None)

    @patch("requests.get")
    def test_alert_endpoint_success(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "forecast": {
                "forecastday": [{"day": {"condition": {"text": "Sunny", "code": 1000}}}]
            }
        }
        mock_get.return_value = mock_response

        # Test the endpoint
        data = {"email": "nsfranco21@gmail.com", "location": "New York"}
        response = self.app.post("/alert", json=data)

        # Enhanced assertions on response
        self.assertEqual(response.status_code, 200)
        self.assertIn("buyer_notification", response.json)
        self.assertIn("forecast_code", response.json)
        self.assertEqual(response.json["forecast_description"], "Sunny")

    def test_alert_endpoint_failure(self):
        # Test the endpoint with invalid input
        data = {"email": "invalid_email", "location": "New York"}
        response = self.app.post("/alert", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_notifications_endpoint_success(self):
        # Test the endpoint with valid input
        email = "test@example.com"
        response = self.app.get(f"/notifications?email={email}")

        # Enhanced assertions on response
        self.assertEqual(response.status_code, 200)
        self.assertIn("notifications", response.json)

    def test_notifications_endpoint_failure(self):
        # Test the endpoint with invalid input (missing email param)
        response = self.app.get("/notifications")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
