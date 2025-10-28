from flask import jsonify
from flask_jwt_extended import create_access_token

from api.authentication.models import User, AuthToken
from core.types import api_response
from core.utils import bcrypt, error_response, success_response, send_email
import os

def register(data: dict) -> api_response:
    password = data.get("password")
    email = data.get("email")
    verify_email_link = os.getenv("FRONT_END_URL", "http://localhost:3000")

    # Validando informações faltantes
    if not all([email, password]):
        return error_response("Campos obrigatórios: email, username, password", 400)

    # Validando email
    email_lower = email.lower()
    if not isinstance(email, str):
        return error_response("Email inválido", 422)
    
    elif not (
        email_lower.endswith("@al.insper.edu.br")
        or email_lower.endswith("@insper.edu.br")
    ):
        return error_response("Email deve ser do Insper", 422)
    
    # Extraindo username do email (parte antes do @)
    username = email.split("@")[0]

    # Validando se usuario já existe
    if User.objects(_email=email):
        return error_response("Usuario ja existe", 400)

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(_username=username, _password=hashed, _email=email)
    new_user.save()
    auth_token = AuthToken(
        _user=new_user,
        _token_type="email_verification",
        _expiration_time=3600,  # 1 hora
    )
    auth_token.save()

    result = send_email(
        to_email=new_user.email,
        subject="Verificação de Email - Progef Metagil",
        template_html="verify_email",
        context={"verification_link": f"{verify_email_link}/verify?authToken={auth_token.id}"},)

    if not result:
        return error_response("Erro ao enviar email de verificação", 500)

    return success_response(message="Usuario registrado, email de verificação enviado!", status_code=201)


def verify_email(data: dict) -> api_response:
    auth_token = data.get("authToken")

    if not auth_token:
        return error_response("Token é obrigatório", 400)
    
    # Verificando token
    try:
        token = AuthToken.objects(id=auth_token).first()
        if not token or token.type != "email_verification":
            token = None
    except Exception:
        token = None
    if not token:
        return error_response("Token de verificação inválido", 400)

    # Verificando se o token já foi usado
    if token.is_used():
        return error_response("Token de verificação já utilizado", 400)
    
    # Verificando se o token expirou
    if token.is_expired():
        return error_response("Token de verificação expirado", 400)

    # Marcando o token como utilizado
    token.mark_used()

    user = token.get_user()
    if not user:
        return error_response("Usuario não encontrado", 404)
    user.activate()

    return success_response(message="Email verificado com sucesso!", status_code=200)

def resend_verification(data: dict) -> api_response:
    email = data.get("email")
    verify_email_link = os.getenv("FRONT_END_URL", "http://localhost:3000")

    if not email:
        return error_response("Email é obrigatório", 400)

    user = User.objects(_email=email).first()
    if not user:
        return error_response("Usuario não encontrado", 404)
    
    if user.is_active():
        return error_response("Email já verificado", 400)

    token = AuthToken.objects(_user=user).order_by("-_created_at").first()
    if token and token.type != "email_verification":
        token = None
    
    if token and not token.is_used() and not token.is_expired():
        # Se o token existe e não foi usado ou expirado, reutilizamos ele
        auth_token = token
    else:
        # Caso contrário, criamos um novo token
        auth_token = AuthToken(
            _user=user,
            _token_type="email_verification",
            _expiration_time=3600,  # 1 hora
        )
    auth_token.save()

    result = send_email(
        to_email=user.email,
        subject="Verificação de Email - Progef Metagil",
        template_html="verify_email",
        context={"verification_link": f"{verify_email_link}/verify?authToken={auth_token.id}"},
    )

    if not result[1] == 200:
        return error_response("Erro ao enviar email de verificação", 500)

    return success_response(message="Email de verificação reenviado com sucesso!", status_code=200)

def login(data: dict) -> api_response:
    email = data.get("email")
    password = data.get("password")

    # Validando informações faltantes
    if not all([email, password]):
        return error_response("Campos obrigatórios: email, password", 400)

    # Validando usuario e senha
    user = User.objects(_email=email).first()
    if not user or not user.check_password(password):
        return error_response("Email ou senha inválidos", 401)
    
    if not user.is_active():
        return error_response("Email não verificado", 403)

    auth_token = create_access_token(identity=user.id.__str__())
    return success_response(data={"access_token": auth_token}, message="Login bem sucedido")

def me(current_user) -> api_response:
    """Get current authenticated user's info."""
    try:
        user = User.objects.get(id=current_user)
        return success_response(data=user.to_dict())
    except User.DoesNotExist:
        return error_response("Usuario não encontrado", 404)
