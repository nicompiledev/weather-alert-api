# Module for retrieving weather information.
#
# This module provides a function to retrieve the weather forecast for a specific location.
#
# Requires:
#     - The WEATHER_API_KEY environment variable with the Weather API key.

import logging
import os
import requests

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Get the Weather API key from the environment variables
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(location):
    """
    Retrieves the weather forecast for a specific location.

    Args:
        location (str): The location for which to retrieve the weather forecast.

    Returns:
        dict: A dictionary containing the weather forecast for the specified location.

    Raises:
        requests.RequestException: If an error occurs while making the request to the Weather API.
    """
    try:
        # Construct the URL for the Weather API request
        url = (
            f"https://api.weatherapi.com/v1/forecast.json?"
            f"key={WEATHER_API_KEY}&"
            f"q={location}&"
            f"days=2&aqi=no&alerts=no&lang=es"
        )

        # Make a GET request to the Weather API
        response = requests.get(url, timeout=10)

        # Raise an exception if the response was not successful
        response.raise_for_status()

        # Return the JSON response from the Weather API
        return response.json()

    except requests.RequestException as e:
        # Log an error message if an exception occurs while making the request
        logger.error("Error fetching weather data: %s", e)
        # Return None to indicate that the request was unsuccessful
        return None
