from flask import Blueprint
from api.health import views as vi

health_bp = Blueprint('health', __name__)


@health_bp.route('/', strict_slashes=False)
def health():
    """Health check endpoint to verify DB connection"""
    return vi.health()

@health_bp.route('/detailed')
def detailed_health():
    """Detailed health check with MongoDB connection test"""
    return vi.detailed_health()