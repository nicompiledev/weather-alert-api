"""
Email module for sending notifications.

This module provides a function for sending emails using a Gmail account.
"""

import smtplib
import os
import logging

# Email configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_email(to_email, subject, body):
    """
    Send an email notification.

    This function sends an email to the specified recipient using the
    configured Gmail account.

    :param to_email: The recipient's email address
    :param subject: The email subject
    :param body: The email body
    :return: None
    """
    try:
        # Establish a connection to the email server
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            # Enable TLS encryption
            server.starttls()
            # Log in to the email account
            server.login(EMAIL_USER, EMAIL_PASS)
            # Construct the email message
            message = f"Subject: {subject}\n\n{body}"
            # Send the email
            server.sendmail(EMAIL_USER, to_email, message.encode("utf-8"))
    except smtplib.SMTPException as e:
        # Log any errors that occur
        logging.error("Error sending email: %s", e)
