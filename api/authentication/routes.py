from flask import Blueprint, request
from api.authentication import views as vi
from flask_jwt_extended import jwt_required, JWTManager
import os
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('authentication', __name__)

bcrypt = Bcrypt()
jwt = JWTManager()




@auth_bp.route("/cadastro", methods=["POST"])
def register():
    data = request.get_json() or {}

    return vi.register(data)
   


@auth_bp.route("/login", methods=["POST"])
def login():
  
    data = request.get_json() or {}
    return vi.login(data)

@auth_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    
    return vi.get_posts()

