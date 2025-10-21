from flask import jsonify
from flask_jwt_extended import create_access_token

from api.authentication.models import User
from core.types import api_response
from core.utils import bcrypt


def register(data: dict) -> api_response:
    password = data.get("password")
    email = data.get("email")

    # Validando informações faltantes
    if not all([email, password]):
        return jsonify({"message": "Campos obrigatórios: email, password"}), 400

    # Validando email
    if not isinstance(email, str):
        return jsonify({"message": "Email inválido"}), 400

    email_lower = email.lower()
    if not (
        email_lower.endswith("@al.insper.edu.br")
        or email_lower.endswith("@insper.edu.br")
    ):
        return jsonify(
            {"message": "Utilize seu email Insper (@al.insper.edu.br ou @insper.edu.br)"}
        ), 400

    # Extraindo username do email (parte antes do @)
    username = email.split("@")[0]

    # Validando se usuario já existe
    if User.objects(email=email):
        return jsonify({"message": "Usuario ja existe"}), 400

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=hashed, email=email)
    new_user.save()
    return jsonify({"message": "Usuario cadastrado com sucesso!"}), 201


def login(data: dict) -> api_response:
    email = data.get("email")
    password = data.get("password")

    # Validando informações faltantes
    if not all([email, password]):
        return jsonify({"message": "Campos obrigatórios: email, password"}), 401

    # Validando usuario e senha
    user = User.objects(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Email ou senha inválidos"}), 401

    token = create_access_token(identity=user.username)
    return jsonify({
        "access_token": token,
        "user": user.to_dict()
    }), 200
