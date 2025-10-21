from flask import request, jsonify
from api.authentication.models import User
from core.types import api_response
from flask_jwt_extended import create_access_token
from core.utils import bcrypt
import mongoengine as me

import os


mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/forum_db')
client = me.connect(host=mongodb_uri)
db = client["fevereiro"]




def register(data: dict) -> api_response:

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    matricula = data.get("matricula")
    name = data.get("name")

    #validando usuario
    if User.objects(email=email):
        return jsonify({'msg': 'Usuario ja existe'}), 400
    
    #validando informações faltantes
    if not all([name, email, username, matricula, password]):
        return jsonify({"msg": "Campos obrigatórios: name, email, username, matricula, password"}), 400
    
    #validando email
    if not isinstance(email, str) or not email.lower().endswith("@al.insper.edu.br"):
        return jsonify({"msg": "Utilize seu email Insper"}), 400
    
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed, email=email, matricula=matricula, name=name)
    new_user.save()
    return jsonify({'msg': 'Usuario cadastrado com sucesso!'}), 201

def login(data: dict) -> api_response: 
    username = data.get("username")
    password = data.get("password")

    #validando usuario e senha
    user = User.objects(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Usuário ou senha inválidos"}), 401
    
    token = create_access_token(identity=username)
    return jsonify(access_token=token), 200
