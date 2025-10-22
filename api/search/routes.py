from flask import Blueprint, request
from api.search import views as vi

search_bp = Blueprint('search', __name__)

# FILTER OPTIONS endpoints

@search_bp.route('/filters/config', methods=['GET'])
def get_filters_config():
    """Get the complete filter configuration."""
    return vi.get_filters_config()

@search_bp.route('/filters/<string:filter_type>', methods=['GET'])
def get_filters_by_type(filter_type):
    """Get filter options by type."""
    return vi.get_filters_by_type(filter_type, request)

@search_bp.route('/search/threads', methods=['GET'])
def search_threads():
    """Search threads by title."""
    return vi.search_threads(request)