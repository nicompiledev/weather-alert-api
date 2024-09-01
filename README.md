# Weather Alert Service

This module implements a Flask web application that provides a weather alert service.

The service fetches weather forecasts for a given location using the WeatherAPI and sends an email notification if adverse weather conditions are predicted that might delay package deliveries.

## Features

- Fetches weather forecasts for a specified location.
- Sends an email alert if certain weather conditions are predicted that could cause delivery delays.

## Prerequisites

- Python 3.7+
- Flask
- Requests
- python-dotenv

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

4. Create a .env file in the root directory with the following variables:

  ```.env
  WEATHER_API_KEY=your_weather_api_key
  EMAIL_USER=your_email@gmail.com
  EMAIL_PASS=your_email_password
  ```
  
## Usage

1. Run the Flask application:

  ```bash
  python app.py
  ```

2. The service will be running on http://127.0.0.1:5000.



## API Endpoints

## POST /alert

This endpoint checks the weather forecast for the specified location and sends an email alert if necessary.

Request Body:

```json

{
    "email": "recipient@example.com",
    "location": "City or latitude,longitude"
}
```

Response:

```json

{
    "forecast_code": 1186,
    "forecast_description": "Partially cloudy",
    "buyer_notification": true
}
```

- forecast_code: The code representing the weather condition for the forecast.

- forecast_description: A description of the forecasted weather condition.

- buyer_notification: Indicates whether the buyer was notified about a possible delay.

## How It Works

- The /alert endpoint accepts a POST request with an email and location.

- The application fetches the weather forecast for the provided location using the WeatherAPI.

- If the forecast predicts adverse weather conditions (codes 1186, 1189, 1192, 1195), an email is sent to the specified address notifying them of potential delivery delays.

- The API response includes the weather condition code, description, and whether an email was sent.

## Notes

- This application uses Gmail's SMTP server for sending emails. Make sure that your Gmail account has Less Secure App Access enabled.

- To improve security, consider using environment variables or a configuration file to store sensitive data like API keys and passwords.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- WeatherAPI for providing weather data.

- Flask for the web framework.
