# Weather Alert Service

This module implements a Flask web application that provides a weather alert service.

The service fetches weather forecasts for a given location using the WeatherAPI and sends an email notification if adverse weather conditions are predicted that might delay package deliveries.

## Features

- Fetches weather forecasts for a specified location.
- Sends an email alert if certain weather conditions are predicted that could cause delivery delays.
- Modular structure for easier maintenance and testing.

## Prerequisites

- Python 3.7+
- Flask
- Requests
- python-dotenv
- SQLite (used for the in-memory database during testing)

## Installation

1. Clone the repository:
   
   ```bash
   git clone https://github.com/nicompiledev/weather-alert-service.git
   cd weather-alert-service
   ```
   
2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:

   ```dotenv
   WEATHER_API_KEY=your_weather_api_key
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_email_password
   FLASK_ENV=development
   ```

   Replace `FLASK_ENV=development` with `FLASK_ENV=production` for production environments.

## Usage

1. Initialize the database (if needed):

   ```bash
   python -c "from app import init_db; init_db()"
   ```

2. Run the Flask application:

   ```bash
   python run.py
   ```

3. The service will be running on http://127.0.0.1:5000.

## Project Structure

```plaintext
weather-alert-service/
│
├── app/
│   ├── __init__.py          # Application factory and database initialization
│   ├── routes/              # Contains API route definitions
│   │   ├── alert.py         # /alert endpoint implementation
│   │   └── notifications.py # /notifications endpoint implementation
│   ├── services/            # Service logic (e.g., weather service, email service)
│   │   ├── weather_service.py
│   │   └── email_service.py
│   └── templates/           # HTML templates (if needed in the future)
│
├── config/
│   └── logging_config.py    # Logging setup for development and production
│
├── tests/                   # Unit tests
│   └── test_app.py          # Test cases for endpoints and services
│
├── .env                     # Environment variables (excluded in .gitignore)
├── requirements.txt         # Python dependencies
├── run.py                   # Entry point to run the application
└── README.md                # Project documentation
```

## API Endpoints

### POST /alert

This endpoint checks the weather forecast for the specified location and sends an email alert if necessary.

**Request Body:**

```json
{
    "email": "recipient@example.com",
    "location": "City or latitude,longitude"
}
```

**Response:**

```json
{
    "forecast_code": 1186,
    "forecast_description": "Parcialmente nublado",
    "buyer_notification": true
}
```

- `forecast_code`: The code representing the weather condition for the forecast.
- `forecast_description`: A description of the forecasted weather condition.
- `buyer_notification`: Indicates whether the buyer was notified about a possible delay.

---

### GET /notifications

This endpoint retrieves all notifications sent to a specific email.

**Query Parameter:**
- `email`: The email address for which to retrieve notifications.

**Response:**

```json
{
    "notifications": [
        {
            "id": 1,
            "email": "recipient@example.com",
            "location": "New York",
            "forecast": "Parcialmente nublado"
        }
    ]
}
```

---

## How It Works

1. **Weather Alerts**: The `/alert` endpoint accepts a POST request with an email and location.
   - Fetches weather data from WeatherAPI.
   - Sends an email if adverse conditions are predicted.
   - Saves the notification in the database.

2. **Notification Retrieval**: The `/notifications` endpoint retrieves saved notifications for a specific email.

3. **Logging**: The application uses a custom logging configuration to handle logs differently for development and production environments.

4. **Modularity**: The application is divided into routes, services, and configuration modules to simplify maintenance and testing.

## Notes

- This application uses Gmail's SMTP server for sending emails. Make sure that your Gmail account has "Less Secure App Access" enabled.
- To enhance security, sensitive credentials should be stored in environment variables or secure storage solutions in production.

## Running Tests

Run the test suite with the following command:

```bash
python -m unittest discover -s tests -p "*.py"
```

This will execute all tests in the `tests/` directory, ensuring the application's functionality.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [WeatherAPI](https://www.weatherapi.com/) for providing weather data.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
```

