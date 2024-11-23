"""
Test suite for the Weather Alert Service application.

This module contains unit tests for the weather alert service application,
including tests for the weather service, Flask endpoints, and database operations.
The tests use an in-memory SQLite database and mock external service calls.

Classes:
    TestWeatherAlertService: Tests for the weather service functionality
    TestFlaskApp: Tests for the Flask application endpoints

Author: [Your Name]
Date: [Current Date]
"""

# Standard library imports
import os
import logging
import unittest
from unittest.mock import patch, MagicMock
import sqlite3

# Third-party imports
import requests

# Local application imports
from app import create_app, init_db


# Configure logging
logging.basicConfig(level=logging.CRITICAL)  # Only CRITICAL messages are shown


class TestWeatherAlertService(unittest.TestCase):
    """
    Test cases for the Weather Alert Service functionality.

    This class contains tests for the weather service operations,
    including successful and failed weather data retrieval.
    """

    def setUp(self):
        """
        Set up test environment before each test.

        Creates an in-memory SQLite database for testing.
        """
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        init_db()  # Initialize the in-memory database

    def tearDown(self):
        """
        Clean up test environment after each test.

        Closes the database connection.
        """
        self.conn.close()

    @patch("requests.get")
    def test_get_weather_success(self, mock_get):
        """
        Test successful weather data retrieval.

        Args:
            mock_get: Mocked requests.get function

        Tests that the weather service successfully retrieves and returns
        weather data when the API call is successful.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "forecast": {
                "forecastday": [{"day": {"condition": {"text": "Sunny", "code": 1000}}}]
            }
        }
        mock_get.return_value = mock_response

        from app.services.weather_service import get_weather

        weather = get_weather("New York")
        self.assertIsNotNone(weather)
        self.assertIn("forecast", weather)

    @patch("requests.get")
    def test_get_weather_failure(self, mock_get):
        """
        Test failed weather data retrieval.

        Args:
            mock_get: Mocked requests.get function

        Tests that the weather service handles API failures gracefully
        and returns None when the API call fails.
        """
        mock_get.side_effect = requests.exceptions.RequestException
        from app.services.weather_service import get_weather

        weather = get_weather("New York")
        self.assertIsNone(weather)


class TestFlaskApp(unittest.TestCase):
    """
    Test cases for the Flask application endpoints.

    This class contains tests for the various Flask endpoints,
    including alert creation and notification retrieval.
    """

    def setUp(self):
        """
        Set up test environment before each test.

        Creates a test Flask client and initializes an in-memory database.
        Sets the TESTING environment variable.
        """
        self.app = create_app().test_client()
        os.environ["TESTING"] = "True"
        self.conn = sqlite3.connect(":memory:")
        init_db()

    def tearDown(self):
        """
        Clean up test environment after each test.

        Closes the database connection and removes the TESTING environment variable.
        """
        self.conn.close()
        os.environ.pop("TESTING", None)

    @patch("app.routes.alert.get_weather")
    @patch("app.routes.alert.send_email")
    @patch("app.routes.alert.save_notification")
    def test_alert_endpoint_success(
        self, mock_save_notification, mock_send_email, mock_get_weather
    ):
        """
        Test successful alert endpoint operation.

        Args:
            mock_save_notification: Mocked save_notification function
            mock_send_email: Mocked send_email function
            mock_get_weather: Mocked get_weather function

        Tests that the alert endpoint successfully processes a valid request
        and returns the expected response.
        """
        mock_get_weather.return_value = {
            "forecast": {
                "forecastday": [{"day": {"condition": {"text": "Sunny", "code": 1000}}}]
            }
        }
        mock_send_email.return_value = None
        mock_save_notification.return_value = None

        data = {"email": "nsfranco21@gmail.com", "location": "New York"}
        response = self.app.post("/alert", json=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("buyer_notification", response.json)
        self.assertIn("forecast_code", response.json)
        self.assertEqual(response.json["forecast_description"], "Sunny")

    @patch("app.routes.alert.get_weather")
    def test_alert_endpoint_failure(self, mock_get_weather):
        """
        Test failed alert endpoint operation.

        Args:
            mock_get_weather: Mocked get_weather function

        Tests that the alert endpoint properly handles and reports errors
        when the weather service fails.
        """
        mock_get_weather.return_value = None

        with self.assertLogs("app.routes.alert", level="ERROR") as log:
            data = {"email": "nsfranco21@gmail.com", "location": "New York"}
            response = self.app.post("/alert", json=data)

            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.json)
            self.assertEqual(response.json["error"], "Failed to fetch weather data")
            self.assertIn("Weather data not available for location", log.output[0])

    def test_notifications_endpoint_success(self):
        """
        Test successful notifications endpoint operation.

        Tests that the notifications endpoint successfully returns
        notifications for a valid email address.
        """
        email = "test@example.com"
        response = self.app.get(f"/notifications?email={email}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("notifications", response.json)

    def test_notifications_endpoint_failure(self):
        """
        Test failed notifications endpoint operation.

        Tests that the notifications endpoint properly handles and reports
        errors when receiving invalid input.
        """
        response = self.app.get("/notifications")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
