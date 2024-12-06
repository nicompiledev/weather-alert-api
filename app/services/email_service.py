"""
Email module for sending notifications.

This module provides a function for sending emails using a Gmail account.
"""

import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_email(to_email, subject, body, content_type="plain"):
    """
    Send an email notification.

    This function sends an email to the specified recipient using the
    configured Gmail account.

    :param to_email: The recipient's email address
    :param subject: The email subject
    :param body: The email body
    :param content_type: The content type of the email body ("plain" for text, "html" for HTML)
    :return: None
    """
    try:
        # Create a MIMEMultipart message
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach the email body with the specified content type
        msg.attach(MIMEText(body, content_type))

        # Establish a connection to the email server
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            # Enable TLS encryption
            server.starttls()
            # Log in to the email account
            server.login(EMAIL_USER, EMAIL_PASS)
            # Send the email
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
            logging.info("Email sent successfully to %s", to_email)
    except smtplib.SMTPException as e:
        # Log any errors that occur
        logging.error("Error sending email: %s", e)
