"""
MongoDB Connection Utility
Simple functions to test and verify MongoDB Atlas connection.
"""

import os
import time
from datetime import datetime

import mongoengine as me
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError

from api.threads.models import Post, Thread
from core.utils import utc_to_brasilia


def test_mongodb_connection(uri=None, timeout=10):
    """
    Test MongoDB connection with detailed feedback.

    Args:
        uri (str): MongoDB connection URI. If None, uses MONGODB_URI env var.
        timeout (int): Connection timeout in seconds.

    Returns:
        dict: Connection test results with status and details.
    """
    if uri is None:
        uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/forum_db")

    is_atlas = "mongodb.net" in uri or "mongodb+srv" in uri

    result = {
        "success": False,
        "is_atlas": is_atlas,
        "connection_type": "MongoDB Atlas" if is_atlas else "Local MongoDB",
        "uri_masked": _mask_uri(uri),
        "server_info": {},
        "performance": {},
        "error": None,
        "troubleshooting": [],
    }

    try:
        # Disconnect any existing connections
        me.disconnect()

        # Measure connection time
        start_time = time.time()

        # Attempt connection with timeout
        connection = me.connect(
            host=uri,
            serverSelectionTimeoutMS=timeout * 1000,
            connectTimeoutMS=timeout * 1000,
            socketTimeoutMS=timeout * 1000,
        )

        connection_time = time.time() - start_time

        # Get server information
        db = connection.get_database()
        server_info = db.client.server_info()

        # Test a simple query
        query_start = time.time()
        Thread.objects().limit(1)
        query_time = time.time() - query_start

        # Populate result
        result.update(
            {
                "success": True,
                "server_info": {
                    "version": server_info.get("version", "Unknown"),
                    "build_info": server_info.get("buildEnvironment", {}),
                },
                "performance": {
                    "connection_time": round(connection_time, 3),
                    "query_time": round(query_time, 3),
                    "connection_rating": _rate_performance(connection_time, is_atlas),
                    "query_rating": _rate_query_performance(query_time, is_atlas),
                },
            }
        )

        return result

    except ServerSelectionTimeoutError as e:
        result["error"] = f"Connection timeout: {str(e)}"
        if is_atlas:
            result["troubleshooting"] = [
                "Check your internet connection",
                "Verify IP address is whitelisted in MongoDB Atlas",
                "Confirm username and password are correct",
                "Check if the cluster is paused or suspended",
                "Verify the connection string format",
            ]
        else:
            result["troubleshooting"] = [
                "Ensure MongoDB is running locally",
                "Check if port 27017 is accessible",
                "Verify MongoDB service is started",
                "Check firewall settings",
            ]
        return result

    except ConfigurationError as e:
        result["error"] = f"Configuration error: {str(e)}"
        result["troubleshooting"] = [
            "Check MONGODB_URI format",
            "Verify connection string syntax",
            "Ensure all required parameters are provided",
        ]
        return result

    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        result["troubleshooting"] = [
            "Check MongoDB server status",
            "Verify network connectivity",
            "Review MongoDB logs for errors",
        ]
        return result

    finally:
        try:
            me.disconnect()
        except:
            pass


def test_database_operations(uri=None):
    """
    Test basic database operations (Create, Read, Update, Delete).

    Args:
        uri (str): MongoDB connection URI.

    Returns:
        dict: Test results for CRUD operations.
    """
    if uri is None:
        uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/forum_db")

    result = {
        "success": False,
        "operations": {
            "create": False,
            "read": False,
            "update": False,
            "delete": False,
            "relationship": False,
        },
        "error": None,
    }

    try:
        # Connect to database
        me.connect(host=uri, serverSelectionTimeoutMS=10000)

        # Test CREATE
        brasilia_now = utc_to_brasilia(datetime.utcnow())
        test_thread = Thread(title=f"Test Thread {brasilia_now.isoformat()}")
        test_thread.save()
        result["operations"]["create"] = True

        # Test READ
        retrieved_thread = Thread.objects.get(id=test_thread.id)
        if retrieved_thread.title == test_thread.title:
            result["operations"]["read"] = True

        # Test relationship CREATE
        test_post = Post(
            thread=test_thread,
            author="Test User",
            content="Test content for connection verification",
        )
        test_post.save()

        # Test relationship READ
        posts = Post.objects(thread=test_thread)
        if len(posts) == 1 and posts[0].author == "Test User":
            result["operations"]["relationship"] = True

        # Test UPDATE
        original_title = test_thread.title
        test_thread.title = f"Updated {original_title}"
        test_thread.save()

        updated_thread = Thread.objects.get(id=test_thread.id)
        if updated_thread.title != original_title:
            result["operations"]["update"] = True

        # Test DELETE
        thread_id = test_thread.id
        test_thread.delete()

        try:
            Thread.objects.get(id=thread_id)
            result["operations"]["delete"] = False
        except me.DoesNotExist:
            result["operations"]["delete"] = True

        # Check if all operations succeeded
        result["success"] = all(result["operations"].values())

    except Exception as e:
        result["error"] = str(e)

    finally:
        try:
            # Clean up any remaining test data
            Thread.objects(title__contains="Test Thread").delete()
            Post.objects(author="Test User").delete()
            me.disconnect()
        except:
            pass

    return result


def _mask_uri(uri):
    """Mask sensitive information in MongoDB URI."""
    if "@" in uri:
        parts = uri.split("@")
        if len(parts) == 2:
            credentials_part = parts[0]
            if "//" in credentials_part:
                protocol_and_creds = credentials_part.split("//")
                if len(protocol_and_creds) == 2 and ":" in protocol_and_creds[1]:
                    user = protocol_and_creds[1].split(":")[0]
                    return f"{protocol_and_creds[0]}//{user}:***@{parts[1]}"
    return uri


def _rate_performance(time_seconds, is_atlas):
    """Rate connection performance."""
    if is_atlas:
        if time_seconds < 2:
            return "Excellent"
        elif time_seconds < 5:
            return "Good"
        elif time_seconds < 10:
            return "Fair"
        else:
            return "Poor"
    else:
        if time_seconds < 0.5:
            return "Excellent"
        elif time_seconds < 1:
            return "Good"
        elif time_seconds < 2:
            return "Fair"
        else:
            return "Poor"


def _rate_query_performance(time_seconds, is_atlas):
    """Rate query performance."""
    if is_atlas:
        if time_seconds < 0.5:
            return "Excellent"
        elif time_seconds < 1:
            return "Good"
        elif time_seconds < 3:
            return "Fair"
        else:
            return "Poor"
    else:
        if time_seconds < 0.1:
            return "Excellent"
        elif time_seconds < 0.3:
            return "Good"
        elif time_seconds < 0.5:
            return "Fair"
        else:
            return "Poor"


def print_connection_report(uri=None):
    """
    Print a detailed connection report to console.

    Args:
        uri (str): MongoDB connection URI.
    """
    print("=" * 60)
    print("🧪 MONGODB CONNECTION TEST REPORT")
    print("=" * 60)

    # Test connection
    conn_result = test_mongodb_connection(uri)

    print("\n🔗 Connection Test:")
    print(f"   Type: {conn_result['connection_type']}")
    print(f"   URI: {conn_result['uri_masked']}")

    if conn_result["success"]:
        print("   Status: ✅ Connected successfully")
        print(
            f"   Server Version: {conn_result['server_info'].get('version', 'Unknown')}"
        )

        perf = conn_result["performance"]
        print("\n⚡ Performance:")
        print(
            f"   Connection Time: {perf['connection_time']}s ({perf['connection_rating']})"
        )
        print(f"   Query Time: {perf['query_time']}s ({perf['query_rating']})")

        # Test database operations
        print("\n📊 Database Operations Test:")
        ops_result = test_database_operations(uri)

        if ops_result["success"]:
            print("   Status: ✅ All operations successful")
            for op, success in ops_result["operations"].items():
                status = "✅" if success else "❌"
                print(f"   {op.capitalize()}: {status}")
        else:
            print("   Status: ❌ Operations failed")
            if ops_result["error"]:
                print(f"   Error: {ops_result['error']}")

    else:
        print("   Status: ❌ Connection failed")
        print(f"   Error: {conn_result['error']}")

        if conn_result["troubleshooting"]:
            print("\n💡 Troubleshooting suggestions:")
            for tip in conn_result["troubleshooting"]:
                print(f"   • {tip}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run the connection test when script is executed directly
    print_connection_report()
