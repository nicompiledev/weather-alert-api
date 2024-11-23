from flask import Blueprint, request, jsonify
from app.services.db_service import get_notifications_by_email
import sqlite3

# Define a Flask Blueprint for handling notifications
notifications_bp = Blueprint("notifications", __name__)


# Define a route for handling GET requests to the notifications endpoint
@notifications_bp.route("", methods=["GET"])
def get_notifications():
    try:
        # Get the 'email' parameter from the request
        email = request.args.get("email")
        if not email:
            # Return an error response if the email parameter is missing
            return jsonify({"error": "Email parameter is required"}), 400

        # Get notifications from the database based on the provided email
        notifications = get_notifications_by_email(email)
        # Return a JSON response with the notifications
        return jsonify({"notifications": notifications})

    except KeyError as e:
        # Log an error and return a 400 response if a KeyError occurs
        print(f"Missing key in request data: {e}")
        return jsonify({"error": "Bad request, missing key"}), 400
    except ValueError as e:
        # Log an error and return a 400 response if a ValueError occurs
        print(f"Value error: {e}")
        return jsonify({"error": "Bad request, invalid value"}), 400
    except sqlite3.DatabaseError as e:
        # Catch SQLite-related errors
        print(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500
    except sqlite3.OperationalError as e:
        # Catch SQLite operational errors (e.g. issues with the SQL query)
        print(f"Database operational error: {e}")
        return jsonify({"error": "Database operational error"}), 500
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500
