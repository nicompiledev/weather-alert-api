import logging
from flask import Blueprint, request, jsonify
from email_validator import validate_email, EmailNotValidError
from app.services.weather_service import get_weather
from app.services.email_service import send_email
from app.services.db_service import save_notification

# Define a Flask Blueprint for handling alerts
alert_bp = Blueprint("alert", __name__)

# Initialize a logger for this module
logger = logging.getLogger(__name__)

# Configure basic logging settings
logging.basicConfig(
    level=logging.DEBUG,  # Change to ERROR or WARNING in production
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# Define a route for handling POST requests to the alert endpoint
@alert_bp.route("", methods=["POST"])
def alert():
    try:
        # Get the JSON data from the request
        data = request.json

        # Extract the email and location from the request data
        email = data["email"]
        location = data["location"]

        # Validate the email address
        try:
            validate_email(email)
        except EmailNotValidError:
            # Return an error response if the email is invalid
            return jsonify({"error": "Invalid email address"}), 400

        # Get the weather data for the specified location
        logger.debug(f"Fetching weather for location: {location}")
        try:
            weather = get_weather(location)
            if not weather:
                # Log an error and return a 500 response if weather data is unavailable
                logger.error(f"Weather data not available for location: {location}")
                return jsonify({"error": "Failed to fetch weather data"}), 500

            # Extract the forecast data from the weather response
            forecast = weather["forecast"]["forecastday"][0]["day"]
            weather_condition = forecast["condition"]["text"]
            forecast_code = forecast["condition"]["code"]

            # Determine whether to notify the buyer based on the weather conditions
            notify_buyer = False
            if forecast_code in [1186, 1189, 1192, 1195, 1063]:
                notify_buyer = True
                # Send an email to the buyer if notification is required
                email_body = (
                    f"Hola! Mañana se espera {weather_condition}, "
                    f"lo que podría retrasar la entrega de tu paquete."
                )
                send_email(
                    email, "ENTREGA RETRASADA POR CONDICIONES CLIMÁTICAS", email_body
                )
                # Save a notification record in the database
                save_notification(email, location, weather_condition)

            # Return a JSON response with the forecast data and notification status
            return jsonify(
                {
                    "forecast_code": forecast_code,
                    "forecast_description": weather_condition,
                    "buyer_notification": notify_buyer,
                }
            )
        except KeyError as e:
            # Log an error and return a 400 response if a KeyError occurs
            logger.error(f"Missing key in weather data: {e}")
            return jsonify({"error": "Bad request, missing key in weather data"}), 400
        except ValueError as e:
            # Log an error and return a 400 response if a ValueError occurs
            logger.error(f"Value error while processing weather data: {e}")
            return jsonify({"error": "Bad request, invalid value in weather data"}), 400
        except (ConnectionError, TimeoutError) as e:
            # Log an error and return a 500 response if a network error occurs
            logger.error(f"Network error: {e}")
            return jsonify({"error": "Network error"}), 500

    except KeyError as e:
        # Log an error and return a 400 response if a KeyError occurs in the request data
        logger.error(f"Missing key in request data: {e}")
        return jsonify({"error": "Bad request, missing key"}), 400
    except ValueError as e:
        # Log an error and return a 400 response if a ValueError occurs in the request data
        logger.error(f"Value error: {e}")
        return jsonify({"error": "Bad request, invalid value"}), 400
    except (ConnectionError, TimeoutError) as e:
        # Log an error and return a 500 response if a network error occurs
        logger.error(f"Network error: {e}")
        return jsonify({"error": "Network error"}), 500
    except Exception as e:
        # Log a critical error and return a 500 response for any unexpected errors
        logger.critical(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500
