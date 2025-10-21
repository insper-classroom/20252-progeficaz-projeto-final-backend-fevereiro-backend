from datetime import datetime
import os
import pytz
import json

# Time Utilities

BRASILIA_TZ = pytz.timezone('America/Sao_Paulo')

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
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    json_data = {   
        "info": {
            "title": "Forum API",
            "version": "1.0.0",
            "description": "API for managing forum threads and search filters"
        },
        "routes": {
            "/": {
                "method": "GET",
                "description": "Basic route for testing",
                "response": {
                    "message": "working"
                }
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
                                "POST": "Confirmation of thread creation"
                            },
                            "url": f"{BASE_URL}/api/threads"
                        },
                        "/threads/<thread_id>": {
                            "methods": ["GET", "PUT", "DELETE"],
                            "description": "Get, update, or delete a specific thread by ID",
                            "response": {
                                "GET": "Details of the specified thread",
                                "PUT": "Confirmation of thread update",
                                "DELETE": "Confirmation of thread deletion"
                            },
                            "url": f"{BASE_URL}/api/threads/<thread_id>"
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
                                    "dateRange": {
                                        "from": "date",
                                        "to": "date"
                                    },
                                    "keywords": ["string"]
                                }
                            },
                            "url": f"{BASE_URL}/api/filters/config"
                        },
                        "/filters/<filter_type>": {
                            "method": "GET",
                            "options": ["semesters", "courses", "subjects"],
                            "description": "Get options for a specific filter type",
                            "response": {
                                "options": ["list of options for the specified filter type"]
                            },
                            "urls": [f"{BASE_URL}/api/filters/semesters",
                                    f"{BASE_URL}/api/filters/courses",
                                    f"{BASE_URL}/api/filters/subjects"]
                        }
                    }
                }
            },
            "/health": {
                "/": {
                    "method": "GET",
                    "description": "Health check endpoint",
                    "response": {
                        "status": "OK"
                    },
                    "url": f"{BASE_URL}/health/"
                },
                "/detailed": {
                    "method": "GET",
                    "description": "Detailed health check endpoint",
                    "response": "A set of health metrics",
                    "url": f"{BASE_URL}/health/detailed"
                }
            }
        }
    }
    with open('core/index.json', 'w') as f:
        json.dump(json_data, f, indent=4)
    return

from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
jwt = JWTManager()