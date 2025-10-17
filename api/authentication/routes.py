from flask import Blueprint, request
from api.authentication import views as vi

auth_bp = Blueprint('authentication', __name__)
