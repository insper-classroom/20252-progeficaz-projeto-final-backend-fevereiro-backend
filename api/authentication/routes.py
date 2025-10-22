from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.authentication import views as vi

auth_bp = Blueprint("authentication", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    return vi.register(data)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    return vi.login(data)

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Get current authenticated user's info."""
    current_user = get_jwt_identity()
    return vi.me(current_user)
