from flask import request, jsonify
from api.reports.models import Report
from api.threads.models import Thread, Post
from mongoengine.errors import DoesNotExist, ValidationError
from core.types import api_response
from core.utils import success_response, error_response
from bson import ObjectId

def create_report(data: dict, current_user: str) -> api_response:
    """Create a new report/denúncia"""
    content_type = data.get('content_type', '').strip().lower()
    content_id = data.get('content_id', '').strip()
    report_type = data.get('report_type', '').strip().lower()
    description = data.get('description', '').strip()
    
    print("DEBUG request data:", repr(data))
    
    # Validações
    if content_type not in ['thread', 'post']:
        return error_response('content_type must be "thread" or "post"', 400)
    
    if not content_id:
        return error_response('content_id is required', 400)
    
    valid_report_types = ['sexual', 'violence', 'discrimination', 'scam', 'self_harm', 'spam', 'other']
    if report_type not in valid_report_types:
        return error_response(f'report_type must be one of: {", ".join(valid_report_types)}', 400)
    
    # Se o tipo for "other", a descrição é obrigatória
    if report_type == 'other' and not description:
        return error_response('description is required when report_type is "other"', 400)
    
    if description and len(description) > 500:
        return error_response('description must be less than 500 characters', 400)
    
    # Verificar se o conteúdo existe
    try:
        if content_type == 'thread':
            Thread.objects.get(id=content_id)
        else:  # post
            Post.objects.get(id=content_id)
    except DoesNotExist:
        return error_response(f'{content_type.capitalize()} not found', 404)
    except Exception:
        return error_response(f'Invalid {content_type} ID', 400)
    
    # Verificar se o usuário já denunciou este conteúdo
    existing_report = Report.objects(
        _reporter=ObjectId(current_user),
        _content_type=content_type,
        _content_id=content_id
    ).first()
    
    if existing_report:
        return error_response('You have already reported this content', 400)
    
    # validação: data pode ser None se o request não enviar JSON válido
    if not data:
        return {"message": "Request body must be valid JSON"}, 400

    # use fallback para evitar AttributeError se description for None
    description = (data.get('description') or '').strip()
    if not description:
        return {"message": "Campo 'description' é obrigatório"}, 400
    
    try:
        report = Report(
            _reporter=ObjectId(current_user),
            _content_type=content_type,
            _content_id=content_id,
            _report_type=report_type,
            _description=description if description else None
        )
        report.save()
        return success_response(
            data=report.to_dict(),
            message="Report created successfully",
            status_code=201
        )
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Failed to create report: {str(e)}", 500)

def list_reports(current_user: str) -> api_response:
    """List all reports (admin only in future)"""
    try:
        reports = Report.objects()
        data = {'reports': [report.to_dict() for report in reports]}
        return success_response(data=data, status_code=200)
    except Exception as e:
        return error_response(f"Failed to retrieve reports: {str(e)}", 500)

def get_report_by_id(report_id: str, current_user: str) -> api_response:
    """Get a specific report by ID"""
    try:
        report = Report.objects.get(id=report_id)
        return success_response(data=report.to_dict(), status_code=200)
    except DoesNotExist:
        return error_response('Report not found', 404)
    except Exception as e:
        return error_response('Invalid report ID', 400)

def test_create_report():
    """Test the creation of a report"""
    # Supondo que você tenha um usuário de teste com ID válido
    test_user_id = "60d5ec49f1a3c30b30f1e4b2"
    
    # Teste 1: Criar um relatório com sucesso
    response = create_report({
        "content_type": "thread",
        "content_id": "60d5ec49f1a3c30b30f1e4b3",
        "report_type": "spam",
        "description": "Este é um teste de relatório"
    }, test_user_id)
    assert response['status_code'] == 201, f"Expected status code 201, got {response['status_code']}"
    
    # Teste 2: Tentar criar um relatório com um tipo de conteúdo inválido
    response = create_report({
        "content_type": "invalid_type",
        "content_id": "60d5ec49f1a3c30b30f1e4b3",
        "report_type": "spam",
        "description": "Este é um teste de relatório"
    }, test_user_id)
    assert response['status_code'] == 400, f"Expected status code 400, got {response['status_code']}"
    
    # Teste 3: Tentar criar um relatório sem fornecer um ID de conteúdo
    response = create_report({
        "content_type": "thread",
        "content_id": "",
        "report_type": "spam",
        "description": "Este é um teste de relatório"
    }, test_user_id)
    assert response['status_code'] == 400, f"Expected status code 400, got {response['status_code']}"
    
    # Teste 4: Tentar criar um relatório com um tipo de relatório inválido
    response = create_report({
        "content_type": "thread",
        "content_id": "60d5ec49f1a3c30b30f1e4b3",
        "report_type": "invalid_type",
        "description": "Este é um teste de relatório"
    }, test_user_id)
    assert response['status_code'] == 400, f"Expected status code 400, got {response['status_code']}"
    
    # Teste 5: Tentar criar um relatório com uma descrição muito longa
    long_description = "a" * 501  # 501 caracteres
    response = create_report({
        "content_type": "thread",
        "content_id": "60d5ec49f1a3c30b30f1e4b3",
        "report_type": "other",
        "description": long_description
    }, test_user_id)
    assert response['status_code'] == 400, f"Expected status code 400, got {response['status_code']}"
    
    # Teste 6: Criar outro relatório com sucesso (para verificar se o mesmo usuário pode criar múltiplos relatórios)
    response = create_report({
        "content_type": "post",
        "content_id": "60d5ec49f1a3c30b30f1e4b4",
        "report_type": "spam",
        "description": "Este é outro teste de relatório"
    }, test_user_id)
    assert response['status_code'] == 201, f"Expected status code 201, got {response['status_code']}"
