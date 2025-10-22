import json
import os
import re
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytz
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

load_dotenv()

# Time Utilities

BRASILIA_TZ = pytz.timezone("America/Sao_Paulo")


def get_brasilia_now():
    """Return current time in Brasília timezone converted to UTC for storage"""
    # Get current time in Brasília
    brasilia_time = datetime.now(BRASILIA_TZ)
    # Convert to UTC for consistent storage
    return brasilia_time.astimezone(pytz.UTC).replace(tzinfo=None)


def utc_to_brasilia(utc_datetime):
    """Convert UTC datetime to Brasília timezone"""
    if utc_datetime is None:
        return None
    # Make UTC datetime timezone-aware
    utc_aware = pytz.UTC.localize(utc_datetime)
    # Convert to Brasília timezone
    return utc_aware.astimezone(BRASILIA_TZ)


def update_index_json() -> None:
    """Update the JSON index file with variables."""
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

    json_data = {
        "info": {
            "title": "Forum API",
            "version": "1.0.0",
            "description": "API for managing forum threads and search filters",
        },
        "routes": {
            "/": {
                "method": "GET",
                "description": "Basic route for testing",
                "response": {"message": "working"},
            },
            "/api": {
                "threads": {
                    "description": "Endpoints related to forum threads",
                    "endpoints": {
                        "/threads": {
                            "methods": ["GET", "POST"],
                            "description": "Get all threads or create a new thread",
                            "response": {
                                "GET": "List of all threads",
                                "POST": "Confirmation of thread creation",
                            },
                            "url": f"{BASE_URL}/api/threads",
                        },
                        "/threads/<thread_id>": {
                            "methods": ["GET", "PUT", "DELETE"],
                            "description": "Get, update, or delete a specific thread by ID",
                            "response": {
                                "GET": "Details of the specified thread",
                                "PUT": "Confirmation of thread update",
                                "DELETE": "Confirmation of thread deletion",
                            },
                            "url": f"{BASE_URL}/api/threads/<thread_id>"
                        },
                        "/posts/<post_id>": {
                            "methods": ["GET", "PUT", "DELETE"],
                            "description": "Get, update, or delete a specific post by ID",
                            "response": {
                                "GET": "Details of the specified post",
                                "PUT": "Confirmation of post update",
                                "DELETE": "Confirmation of post deletion"
                            },
                            "url": f"{BASE_URL}/api/posts/<post_id>"
                        },
                        "/posts/<post_id>/upvote": {
                            "methods": ["POST"],
                            "description": "Upvote a specific post (requires authentication)",
                            "response": {
                                "POST": "Updated vote counts and confirmation"
                            },
                            "url": f"{BASE_URL}/api/posts/<post_id>/upvote"
                        },
                        "/posts/<post_id>/downvote": {
                            "methods": ["POST"],
                            "description": "Downvote a specific post (requires authentication)",
                            "response": {
                                "POST": "Updated vote counts and confirmation"
                            },
                            "url": f"{BASE_URL}/api/posts/<post_id>/downvote"
                        },
                        "/posts/<post_id>/vote": {
                            "methods": ["DELETE"],
                            "description": "Remove user's vote from a specific post (requires authentication)",
                            "response": {
                                "DELETE": "Updated vote counts and confirmation"
                            },
                            "url": f"{BASE_URL}/api/posts/<post_id>/vote"
                        }

                    }
                },
                "search": {
                    "description": "Endpoints for searching threads",
                    "endpoints": {
                        "/filters/config": {
                            "method": "GET",
                            "description": "Get the complete filter configuration",
                            "response": {
                                "filters": {
                                    "author": "string",
                                    "dateRange": {"from": "date", "to": "date"},
                                    "keywords": ["string"],
                                }
                            },
                            "url": f"{BASE_URL}/api/filters/config",
                        },
                        "/filters/<filter_type>": {
                            "method": "GET",
                            "options": ["semesters", "courses", "subjects"],
                            "description": "Get options for a specific filter type",
                            "response": {
                                "options": [
                                    "list of options for the specified filter type"
                                ]
                            },
                            "urls": [
                                f"{BASE_URL}/api/filters/semesters",
                                f"{BASE_URL}/api/filters/courses",
                                f"{BASE_URL}/api/filters/subjects",
                            ],
                        },
                    },
                },
            },
            "/health": {
                "/": {
                    "method": "GET",
                    "description": "Health check endpoint",
                    "response": {"status": "OK"},
                    "url": f"{BASE_URL}/health/",
                },
                "/detailed": {
                    "method": "GET",
                    "description": "Detailed health check endpoint",
                    "response": "A set of health metrics",
                    "url": f"{BASE_URL}/health/detailed",
                },
            },
        },
    }
    with open("core/index.json", "w") as f:
        json.dump(json_data, f, indent=4)
    return


# Auth Utilities


bcrypt = Bcrypt()
jwt = JWTManager()

# API Response Utilities


def success_response(data=None, message=None, status_code=200):
    """Create a standardized success response"""
    from flask import jsonify

    response_data = {}

    if message:
        response_data["message"] = message

    if data is not None:
        response_data.update(data)

    return jsonify(response_data), status_code


def error_response(message, status_code=400, details=None):
    """Create a standardized error response"""
    from flask import jsonify

    response_data = {"error": message}

    if details:
        response_data["details"] = details

    return jsonify(response_data), status_code


def validation_error_response(errors):
    """Create a standardized validation error response"""
    return error_response(message="Validation failed", status_code=422, details=errors)


# email sending utils


def send_email(receiver_email, subject, html=""):
    """
    Send an email with HTML content.

    Args:
        receiver_email (str): The recipient's email address
        subject (str): The email subject
        html (str): The HTML content of the email

    Returns:
        tuple: (response_data, status_code) - HTTP status code
    """

    # Validate input parameters
    if not receiver_email or not subject:
        return {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Receiver email and subject are required",
                "details": "Both receiver_email and subject parameters must be provided",
            }
        }, 400  # Bad Request

    # Validate email format (basic validation)

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, receiver_email):
        return {
            "error": {
                "code": "INVALID_EMAIL_FORMAT",
                "message": "Invalid email format",
                "details": f"The email address '{receiver_email}' is not in a valid format",
            }
        }, 400  # Bad Request

    sender_email = os.environ.get("EMAIL", "example@email.com")
    password = os.environ.get("EMAIL_PASS", "1234567890")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part)

    # Create secure connection with server and send email
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return {
            "data": {
                "email_id": f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "recipient": receiver_email,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "status": "sent",
            },
            "message": "Email sent successfully",
        }, 200  # OK

    except smtplib.SMTPAuthenticationError:
        return {
            "error": {
                "code": "AUTHENTICATION_FAILED",
                "message": "Failed to authenticate with email server",
                "details": "Invalid email credentials or authentication method",
            }
        }, 401  # Unauthorized

    except smtplib.SMTPRecipientsRefused:
        return {
            "error": {
                "code": "RECIPIENT_REFUSED",
                "message": "Recipient email address was refused by the server",
                "details": f"The email address '{receiver_email}' was rejected by the SMTP server",
            }
        }, 422  # Unprocessable Entity

    except smtplib.SMTPException as e:
        return {
            "error": {
                "code": "SMTP_ERROR",
                "message": "SMTP server error occurred",
                "details": str(e),
            }
        }, 502  # Bad Gateway

    except Exception as e:
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while sending email",
                "details": str(e),
            }
        }, 500  # Internal Server Error
