"""
Tests for the Reports/Denúncias system.
"""
import pytest
from api.reports.models import Report
from api.threads.models import Thread, Post


@pytest.fixture
def report_data():
    """Fixture for common report data."""
    return {
        "content_type": "thread",
        "content_id": "",  # Will be filled in tests
        "report_type": "spam",
        "description": "This content is spam and should be removed"
    }


@pytest.fixture
def thread_to_report(client, registered_user_token, thread_data):
    """Fixture to create a thread that can be reported."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    response = client.post('/api/threads', json=thread_data, headers=headers)
    assert response.status_code == 201
    return response.json['id']


@pytest.fixture
def post_to_report(client, registered_user_token, thread_data, post_data):
    """Fixture to create a post that can be reported."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}

    # Create thread first
    thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = thread_response.json['id']

    # Create post
    post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    assert post_response.status_code == 201
    return post_response.json['id']


class TestCreateReport:
    """Tests for creating reports."""

    def test_create_report_for_thread_success(self, client, other_user_token, thread_to_report, report_data):
        """Test successful creation of a report for a thread."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report
        report_data['content_type'] = 'thread'

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 201
        assert response.json['content_type'] == 'thread'
        assert response.json['content_id'] == thread_to_report
        assert response.json['report_type'] == 'spam'
        assert response.json['status'] == 'pending'
        assert 'id' in response.json
        assert 'reporter' in response.json
        assert 'created_at' in response.json

        # Verify report is in database
        report = Report.objects.get(id=response.json['id'])
        assert report is not None
        assert report.content_type == 'thread'
        assert report.status == 'pending'

    def test_create_report_for_post_success(self, client, other_user_token, post_to_report, report_data):
        """Test successful creation of a report for a post."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = post_to_report
        report_data['content_type'] = 'post'

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 201
        assert response.json['content_type'] == 'post'
        assert response.json['content_id'] == post_to_report
        assert response.json['report_type'] == 'spam'

    def test_create_report_with_type_sexual(self, client, other_user_token, thread_to_report):
        """Test creating report with sexual content type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        data = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "sexual",
            "description": "Contains explicit sexual content"
        }

        response = client.post('/api/reports', json=data, headers=headers)
        assert response.status_code == 201
        assert response.json['report_type'] == 'sexual'

    def test_create_report_with_type_violence(self, client, other_user_token, thread_to_report):
        """Test creating report with violence type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        data = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "violence",
            "description": "Contains violent threats"
        }

        response = client.post('/api/reports', json=data, headers=headers)
        assert response.status_code == 201
        assert response.json['report_type'] == 'violence'

    def test_create_report_with_type_discrimination(self, client, other_user_token, thread_to_report):
        """Test creating report with discrimination type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        data = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "discrimination",
            "description": "Contains discriminatory content"
        }

        response = client.post('/api/reports', json=data, headers=headers)
        assert response.status_code == 201
        assert response.json['report_type'] == 'discrimination'

    def test_create_report_with_type_scam(self, client, other_user_token, thread_to_report):
        """Test creating report with scam type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        data = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "scam"
        }

        response = client.post('/api/reports', json=data, headers=headers)
        assert response.status_code == 201
        assert response.json['report_type'] == 'scam'

    def test_create_report_with_type_self_harm(self, client, other_user_token, thread_to_report):
        """Test creating report with self_harm type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        data = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "self_harm"
        }

        response = client.post('/api/reports', json=data, headers=headers)
        assert response.status_code == 201
        assert response.json['report_type'] == 'self_harm'

    def test_create_report_with_type_other_with_description(self, client, other_user_token, thread_to_report):
        """Test creating report with 'other' type requires description."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        data = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "other",
            "description": "This is another type of problem not listed"
        }

        response = client.post('/api/reports', json=data, headers=headers)
        assert response.status_code == 201
        assert response.json['report_type'] == 'other'
        assert response.json['description'] == data['description']

    def test_create_report_with_type_other_without_description(self, client, other_user_token, thread_to_report):
        """Test creating report with 'other' type without description fails."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        data = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "other"
        }

        response = client.post('/api/reports', json=data, headers=headers)
        assert response.status_code == 400
        assert 'description' in response.json['error'].lower() or 'other' in response.json['error'].lower()


class TestCreateReportValidation:
    """Tests for report creation validation."""

    def test_create_report_unauthorized(self, client, thread_to_report, report_data):
        """Test creating report without authentication."""
        report_data['content_id'] = thread_to_report
        response = client.post('/api/reports', json=report_data)
        assert response.status_code == 401
        assert response.json == {'msg': 'Missing Authorization Header'}

    def test_create_report_missing_content_type(self, client, other_user_token, thread_to_report, report_data):
        """Test creating report without content_type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report
        del report_data['content_type']

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 400

    def test_create_report_missing_content_id(self, client, other_user_token, report_data):
        """Test creating report without content_id."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        del report_data['content_id']

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 400

    def test_create_report_missing_report_type(self, client, other_user_token, thread_to_report, report_data):
        """Test creating report without report_type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report
        del report_data['report_type']

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 400

    def test_create_report_invalid_content_type(self, client, other_user_token, thread_to_report, report_data):
        """Test creating report with invalid content_type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report
        report_data['content_type'] = 'invalid_type'

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 400

    def test_create_report_invalid_report_type(self, client, other_user_token, thread_to_report, report_data):
        """Test creating report with invalid report_type."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report
        report_data['report_type'] = 'invalid_report_type'

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 400

    def test_create_report_non_existent_thread(self, client, other_user_token, report_data):
        """Test creating report for non-existent thread."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = '507f1f77bcf86cd799439011'  # Valid ID format but non-existent
        report_data['content_type'] = 'thread'

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 404

    def test_create_report_non_existent_post(self, client, other_user_token, report_data):
        """Test creating report for non-existent post."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = '507f1f77bcf86cd799439011'  # Valid ID format but non-existent
        report_data['content_type'] = 'post'

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 404

    def test_create_report_invalid_content_id_format(self, client, other_user_token, report_data):
        """Test creating report with invalid content_id format."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = 'invalid-id-format'

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 400

    def test_create_duplicate_report(self, client, other_user_token, thread_to_report, report_data):
        """Test creating duplicate report for same content by same user."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report

        # First report
        response1 = client.post('/api/reports', json=report_data, headers=headers)
        assert response1.status_code == 201

        # Duplicate report
        response2 = client.post('/api/reports', json=report_data, headers=headers)
        assert response2.status_code == 400
        assert 'already reported' in response2.json['error'].lower()

    def test_create_report_description_too_long(self, client, other_user_token, thread_to_report, report_data):
        """Test creating report with description exceeding 500 characters."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report
        report_data['description'] = 'x' * 501  # 501 characters

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 400


class TestListReports:
    """Tests for listing reports."""

    def test_list_reports_empty(self, client, registered_user_token):
        """Test listing reports when there are none."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/reports', headers=headers)
        assert response.status_code == 200
        assert 'reports' in response.json
        assert isinstance(response.json['reports'], list)
        assert len(response.json['reports']) == 0

    def test_list_reports_with_reports(self, client, other_user_token, thread_to_report, report_data):
        """Test listing reports when there are reports."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report

        # Create first report
        response1 = client.post('/api/reports', json=report_data, headers=headers)
        assert response1.status_code == 201

        # List reports
        response = client.get('/api/reports', headers=headers)
        assert response.status_code == 200
        assert 'reports' in response.json
        assert len(response.json['reports']) == 1
        assert response.json['reports'][0]['id'] == response1.json['id']

    def test_list_reports_multiple(self, client, other_user_token, thread_to_report, post_to_report):
        """Test listing multiple reports."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Create report for thread
        thread_report = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "spam",
            "description": "Thread spam"
        }
        response1 = client.post('/api/reports', json=thread_report, headers=headers)
        assert response1.status_code == 201

        # Create report for post
        post_report = {
            "content_type": "post",
            "content_id": post_to_report,
            "report_type": "violence",
            "description": "Post violence"
        }
        response2 = client.post('/api/reports', json=post_report, headers=headers)
        assert response2.status_code == 201

        # List reports
        response = client.get('/api/reports', headers=headers)
        assert response.status_code == 200
        assert len(response.json['reports']) == 2

    def test_list_reports_unauthorized(self, client):
        """Test listing reports without authentication."""
        response = client.get('/api/reports')
        assert response.status_code == 401
        assert response.json == {'msg': 'Missing Authorization Header'}

    def test_list_reports_ordered_by_date(self, client, other_user_token, thread_to_report, post_to_report):
        """Test that reports are ordered by creation date (most recent first)."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Create first report
        report1 = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "spam"
        }
        response1 = client.post('/api/reports', json=report1, headers=headers)
        assert response1.status_code == 201

        # Create second report
        report2 = {
            "content_type": "post",
            "content_id": post_to_report,
            "report_type": "violence"
        }
        response2 = client.post('/api/reports', json=report2, headers=headers)
        assert response2.status_code == 201

        # List reports
        response = client.get('/api/reports', headers=headers)
        assert response.status_code == 200
        reports = response.json['reports']

        # Second report should appear first (most recent)
        assert reports[0]['id'] == response2.json['id']
        assert reports[1]['id'] == response1.json['id']


class TestGetReportById:
    """Tests for getting a specific report."""

    def test_get_report_by_id_success(self, client, other_user_token, thread_to_report, report_data):
        """Test getting a report by ID."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report

        # Create report
        create_response = client.post('/api/reports', json=report_data, headers=headers)
        assert create_response.status_code == 201
        report_id = create_response.json['id']

        # Get report by ID
        response = client.get(f'/api/reports/{report_id}', headers=headers)
        assert response.status_code == 200
        assert response.json['id'] == report_id
        assert response.json['content_type'] == 'thread'
        assert response.json['report_type'] == 'spam'
        assert 'reporter' in response.json
        assert 'created_at' in response.json

    def test_get_report_non_existent(self, client, registered_user_token):
        """Test getting a non-existent report."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/reports/507f1f77bcf86cd799439011', headers=headers)
        assert response.status_code == 404

    def test_get_report_invalid_id_format(self, client, registered_user_token):
        """Test getting a report with invalid ID format."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/reports/invalid-id', headers=headers)
        assert response.status_code == 400

    def test_get_report_unauthorized(self, client, other_user_token, thread_to_report, report_data):
        """Test getting a report without authentication."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report

        # Create report
        create_response = client.post('/api/reports', json=report_data, headers=headers)
        report_id = create_response.json['id']

        # Try to get without auth
        response = client.get(f'/api/reports/{report_id}')
        assert response.status_code == 401
        assert response.json == {'msg': 'Missing Authorization Header'}


class TestReportStatuses:
    """Tests for report status field."""

    def test_report_initial_status_is_pending(self, client, other_user_token, thread_to_report, report_data):
        """Test that new reports have 'pending' status."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report

        response = client.post('/api/reports', json=report_data, headers=headers)
        assert response.status_code == 201
        assert response.json['status'] == 'pending'

    def test_report_status_in_list(self, client, other_user_token, thread_to_report, report_data):
        """Test that report status appears in list."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        report_data['content_id'] = thread_to_report

        # Create report
        client.post('/api/reports', json=report_data, headers=headers)

        # List reports
        response = client.get('/api/reports', headers=headers)
        assert response.status_code == 200
        assert response.json['reports'][0]['status'] == 'pending'


class TestReportIntegration:
    """Integration tests for reports."""

    def test_multiple_users_can_report_same_content(self, client, registered_user_token, other_user_token, thread_to_report):
        """Test that multiple users can report the same content."""
        report_data = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "spam",
            "description": "This is spam"
        }

        # First user reports
        headers1 = {'Authorization': f'Bearer {registered_user_token}'}
        response1 = client.post('/api/reports', json=report_data, headers=headers1)
        assert response1.status_code == 201

        # Second user reports same content
        headers2 = {'Authorization': f'Bearer {other_user_token}'}
        response2 = client.post('/api/reports', json=report_data, headers=headers2)
        assert response2.status_code == 201

        # Verify two different reports exist
        assert response1.json['id'] != response2.json['id']

    def test_report_thread_and_post_from_same_thread(self, client, other_user_token, thread_to_report, post_to_report):
        """Test reporting both a thread and a post from the same thread."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Report thread
        thread_report = {
            "content_type": "thread",
            "content_id": thread_to_report,
            "report_type": "spam"
        }
        response1 = client.post('/api/reports', json=thread_report, headers=headers)
        assert response1.status_code == 201

        # Report post
        post_report = {
            "content_type": "post",
            "content_id": post_to_report,
            "report_type": "violence"
        }
        response2 = client.post('/api/reports', json=post_report, headers=headers)
        assert response2.status_code == 201

        # Both should succeed
        assert response1.json['id'] != response2.json['id']
