from bson import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError

from api.reports.models import Report
from api.threads.models import Post, Thread
from core.types import api_response
from core.utils import error_response, success_response


def create_report(data: dict, current_user: str) -> api_response:
    """Create a new report/denúncia"""
    content_type = data.get("content_type", "").strip().lower()
    content_id = data.get("content_id", "").strip()
    report_type = data.get("report_type", "").strip().lower()
    description = data.get("description", "").strip()

    print("DEBUG request data:", repr(data))

    # Validações
    if content_type not in ["thread", "post"]:
        return error_response('content_type must be "thread" or "post"', 400)

    if not content_id:
        return error_response("content_id is required", 400)

    valid_report_types = [
        "sexual",
        "violence",
        "discrimination",
        "scam",
        "self_harm",
        "spam",
        "other",
    ]
    if report_type not in valid_report_types:
        return error_response(
            f"report_type must be one of: {', '.join(valid_report_types)}", 400
        )

    # Se o tipo for "other", a descrição é obrigatória
    if report_type == "other" and not description:
        return error_response(
            'description is required when report_type is "other"', 400
        )

    if description and len(description) > 500:
        return error_response("description must be less than 500 characters", 400)

    # Verificar se o conteúdo existe
    try:
        if content_type == "thread":
            Thread.objects.get(id=content_id)
        else:  # post
            Post.objects.get(id=content_id)
    except DoesNotExist:
        return error_response(f"{content_type.capitalize()} not found", 404)
    except Exception:
        return error_response(f"Invalid {content_type} ID", 400)

    # Verificar se o usuário já denunciou este conteúdo
    existing_report = Report.objects(
        _reporter=ObjectId(current_user),
        _content_type=content_type,
        _content_id=content_id,
    ).first()

    if existing_report:
        return error_response("You have already reported this content", 400)

    try:
        report = Report(
            _reporter=ObjectId(current_user),
            _content_type=content_type,
            _content_id=content_id,
            _report_type=report_type,
            _description=description if description else None,
        )
        report.save()
        return success_response(
            data=report.to_dict(),
            message="Report created successfully",
            status_code=201,
        )
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Failed to create report: {str(e)}", 500)


def list_reports(current_user: str) -> api_response:
    """List all reports (admin only in future)"""
    try:
        reports = Report.objects()
        data = {"reports": [report.to_dict() for report in reports]}
        return success_response(data=data, status_code=200)
    except Exception as e:
        return error_response(f"Failed to retrieve reports: {str(e)}", 500)


def get_report_by_id(report_id: str, current_user: str) -> api_response:
    """Get a specific report by ID"""
    try:
        report = Report.objects.get(id=report_id)
        return success_response(data=report.to_dict(), status_code=200)
    except DoesNotExist:
        return error_response("Report not found", 404)
    except Exception:
        return error_response("Invalid report ID", 400)
