from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.reports import views as vi

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    """Create a new report/denúncia"""
    data = request.get_json() or {}
    current_user = get_jwt_identity()
    return vi.create_report(data, current_user)

@reports_bp.route('/reports', methods=['GET'])
@jwt_required()
def list_reports():
    """List all reports (for admin purposes)"""
    current_user = get_jwt_identity()
    return vi.list_reports(current_user)

@reports_bp.route('/reports/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get a specific report by ID"""
    current_user = get_jwt_identity()
    return vi.get_report_by_id(report_id, current_user)
