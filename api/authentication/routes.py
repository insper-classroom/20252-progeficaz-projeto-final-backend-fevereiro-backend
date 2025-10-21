from flask import Blueprint, request
from api.authentication import views as vi
from flask_jwt_extended import jwt_required
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('authentication', __name__)




@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    return vi.register(data)
   


@auth_bp.route("/login", methods=["POST"])
def login():
  
    data = request.get_json() or {}
    return vi.login(data)


