from flask import jsonify
from flask_jwt_extended import create_access_token

from api.authentication.models import User
from core.types import api_response
from core.utils import bcrypt, error_response, success_response, validation_error_response


def register(data: dict) -> api_response:
    password = data.get("password")
    email = data.get("email")

    # Validando informações faltantes
    errors = {}
    if not all([email, password]):
        errors["fields"] = "Campos obrigatórios: email, password"

    # Validando email
    email_lower = email.lower()
    if not isinstance(email, str):
        errors["email"] = "Email inválido"  
    
    elif not (
        email_lower.endswith("@al.insper.edu.br")
        or email_lower.endswith("@insper.edu.br")
    ):
        errors["email"] = "Email deve ser do Insper"

    # Extraindo username do email (parte antes do @)
    username = email.split("@")[0]

    # Validando se usuario já existe
    if User.objects(email=email):
        errors["email"] = "Usuario ja existe"

    if errors:
        return validation_error_response(errors)

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=hashed, email=email)
    new_user.save()
    return success_response(message="Usuario registrado com sucesso", status_code=201)


def login(data: dict) -> api_response:
    email = data.get("email")
    password = data.get("password")

    errors = {}
    # Validando informações faltantes
    if not all([email, password]):
        errors["fields"] = "Campos obrigatórios: email, password"

    # Validando usuario e senha
    user = User.objects(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        errors["credentials"] = "Email ou senha inválidos"

    if errors:
        return validation_error_response(errors)
    print("login successful for user:", user.id)
    token = create_access_token(identity=user.id.__str__())
    return success_response(data={"access_token": token}, message="Login bem sucedido")

def me(current_user) -> api_response:
    """Get current authenticated user's info."""
    try:
        user = User.objects.get(id=current_user)
        return success_response(data=user.to_dict())
    except User.DoesNotExist:
        return error_response("User not found", 404)