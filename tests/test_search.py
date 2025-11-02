"""
Tests for the Search and Filters system.
"""
import pytest


@pytest.fixture
def threads_for_search(client, registered_user_token, thread_data):
    """Create multiple threads for search tests."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}

    threads = [
        {
            **thread_data,
            "title": "Como implementar autenticação JWT em Flask?",
            "semester": 3,
            "courses": ["cc"],
            "subjects": ["Programação Eficaz"]
        },
        {
            **thread_data,
            "title": "Dúvida sobre banco de dados relacionais",
            "semester": 3,
            "courses": ["cc"],
            "subjects": ["Banco de Dados"]
        },
        {
            **thread_data,
            "title": "JWT vs Session: qual usar?",
            "semester": 3,
            "courses": ["cc"],
            "subjects": ["Programação Eficaz"]
        },
        {
            **thread_data,
            "title": "Como calcular ROI em marketing digital",
            "semester": 3,
            "courses": ["adm"],
            "subjects": ["Marketing"]
        }
    ]

    thread_ids = []
    for thread in threads:
        response = client.post('/api/threads', json=thread, headers=headers)
        assert response.status_code == 201
        thread_ids.append(response.json['id'])

    return thread_ids


class TestFilterConfig:
    """Tests for filter configuration endpoint."""

    def test_get_filter_config_success(self, client, registered_user_token):
        """Test getting filter configuration."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/config', headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json, dict)

        # Check structure
        assert 'semester' in response.json
        assert 'course' in response.json
        assert 'subject' in response.json

    def test_filter_config_semester_structure(self, client, registered_user_token):
        """Test semester filter configuration structure."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/config', headers=headers)

        semester = response.json['semester']
        assert 'required' in semester
        assert 'multiple' in semester
        assert 'options' in semester
        assert isinstance(semester['options'], list)
        assert len(semester['options']) == 10  # 10 semesters

        # Check semester option structure
        assert 'id' in semester['options'][0]
        assert 'name' in semester['options'][0]

    def test_filter_config_course_structure(self, client, registered_user_token):
        """Test course filter configuration structure."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/config', headers=headers)

        course = response.json['course']
        assert 'required' in course
        assert 'multiple' in course
        assert 'options' in course
        assert isinstance(course['options'], list)
        assert len(course['options']) == 9  # 9 courses

        # Check course option structure
        assert 'id' in course['options'][0]
        assert 'name' in course['options'][0]

    def test_filter_config_subject_structure(self, client, registered_user_token):
        """Test subject filter configuration structure."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/config', headers=headers)

        subject = response.json['subject']
        assert 'required' in subject
        assert 'multiple' in subject
        assert 'searchable' in subject
        assert 'depends_on' in subject
        assert 'options' in subject
        assert isinstance(subject['options'], dict)

        # Check that subjects are organized by course
        assert 'cc' in subject['options']
        assert 'adm' in subject['options']

    def test_filter_config_unauthorized(self, client):
        """Test getting filter config without authentication."""
        response = client.get('/api/filters/config')
        assert response.status_code == 401


class TestGetSemesters:
    """Tests for getting semester options."""

    def test_get_semesters_success(self, client, registered_user_token):
        """Test getting semester options."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/semesters', headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 10

        # Check structure
        assert 'id' in response.json[0]
        assert 'name' in response.json[0]
        assert response.json[0]['id'] == 1
        assert '1º Semestre' in response.json[0]['name']

    def test_semesters_ordered_correctly(self, client, registered_user_token):
        """Test that semesters are ordered 1-10."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/semesters', headers=headers)

        semesters = response.json
        for i, semester in enumerate(semesters, start=1):
            assert semester['id'] == i


class TestGetCourses:
    """Tests for getting course options."""

    def test_get_courses_success(self, client, registered_user_token):
        """Test getting course options."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/courses', headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 9  # 9 courses

        # Check structure
        assert 'id' in response.json[0]
        assert 'name' in response.json[0]

    def test_courses_include_all_types(self, client, registered_user_token):
        """Test that all expected courses are present."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/courses', headers=headers)

        course_ids = [c['id'] for c in response.json]
        expected_courses = ['cc', 'adm', 'eng_civil', 'eng_mec', 'eng_ele', 'eng_comp', 'direito', 'medicina', 'psicologia']

        for expected in expected_courses:
            assert expected in course_ids


class TestGetSubjects:
    """Tests for getting subject options."""

    def test_get_subjects_all(self, client, registered_user_token):
        """Test getting all subjects without filters."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/subjects', headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

    def test_get_subjects_by_course(self, client, registered_user_token):
        """Test getting subjects filtered by course."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/subjects?courses=cc', headers=headers)

        assert response.status_code == 200
        subjects = response.json

        # Should include CC subjects
        assert any('Programação' in s for s in subjects)
        assert any('Algoritmos' in s for s in subjects)

    def test_get_subjects_by_semester(self, client, registered_user_token):
        """Test getting subjects filtered by semester."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/subjects?semester=3', headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json, list)

    def test_get_subjects_by_course_and_semester(self, client, registered_user_token):
        """Test getting subjects filtered by course and semester."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/subjects?courses=cc&semester=3', headers=headers)

        assert response.status_code == 200
        subjects = response.json

        # Should include semester 3 CC subjects
        expected_subjects = ["Algoritmos e Complexidade", "Banco de Dados", "Programação Eficaz"]
        for expected in expected_subjects:
            assert expected in subjects

    def test_get_subjects_by_multiple_courses(self, client, registered_user_token):
        """Test getting subjects for multiple courses."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/subjects?courses=cc&courses=adm&semester=3', headers=headers)

        assert response.status_code == 200
        subjects = response.json

        # Should include subjects from both courses
        assert len(subjects) > 0

    def test_search_subjects_by_query(self, client, registered_user_token):
        """Test searching subjects by query string."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/subjects?q=programação', headers=headers)

        assert response.status_code == 200
        subjects = response.json

        # All results should contain "programação" (case-insensitive)
        for subject in subjects:
            assert 'programação' in subject.lower() or 'programacao' in subject.lower()

    def test_search_subjects_case_insensitive(self, client, registered_user_token):
        """Test that subject search is case-insensitive."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}

        # Try different cases
        response1 = client.get('/api/filters/subjects?q=banco', headers=headers)
        response2 = client.get('/api/filters/subjects?q=BANCO', headers=headers)
        response3 = client.get('/api/filters/subjects?q=BaNcO', headers=headers)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # All should return same results
        assert len(response1.json) == len(response2.json) == len(response3.json)

    def test_subjects_sorted_alphabetically(self, client, registered_user_token):
        """Test that subjects are sorted alphabetically."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/subjects', headers=headers)

        subjects = response.json
        assert subjects == sorted(subjects)

    def test_subjects_no_duplicates(self, client, registered_user_token):
        """Test that subject list has no duplicates."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/filters/subjects', headers=headers)

        subjects = response.json
        assert len(subjects) == len(set(subjects))


class TestSearchThreads:
    """Tests for searching threads."""

    def test_search_threads_success(self, client, registered_user_token, threads_for_search):
        """Test successful thread search."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/search/threads?q=JWT', headers=headers)

        assert response.status_code == 200
        assert 'query' in response.json
        assert 'count' in response.json
        assert 'results' in response.json
        assert response.json['query'] == 'JWT'
        assert response.json['count'] >= 2  # At least 2 threads with "JWT"

    def test_search_threads_case_insensitive(self, client, registered_user_token, threads_for_search):
        """Test that search is case-insensitive."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}

        response1 = client.get('/api/search/threads?q=jwt', headers=headers)
        response2 = client.get('/api/search/threads?q=JWT', headers=headers)
        response3 = client.get('/api/search/threads?q=Jwt', headers=headers)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # All should return same number of results
        assert response1.json['count'] == response2.json['count'] == response3.json['count']

    def test_search_threads_with_semester_filter(self, client, registered_user_token, threads_for_search):
        """Test searching with semester filter."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/search/threads?q=banco&semester=3', headers=headers)

        assert response.status_code == 200
        results = response.json['results']

        # All results should be from semester 3
        for result in results:
            assert result['semester'] == 3

    def test_search_threads_with_course_filter(self, client, registered_user_token, threads_for_search):
        """Test searching with course filter."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/search/threads?q=a&courses=cc', headers=headers)

        assert response.status_code == 200
        results = response.json['results']

        # All results should be from CC course
        for result in results:
            assert 'cc' in result['courses']

    def test_search_threads_with_subject_filter(self, client, registered_user_token, threads_for_search):
        """Test searching with subject filter."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/search/threads?q=JWT&subjects=Programação Eficaz', headers=headers)

        assert response.status_code == 200
        results = response.json['results']

        # All results should have the subject
        for result in results:
            assert 'Programação Eficaz' in result['subjects']

    def test_search_threads_with_multiple_filters(self, client, registered_user_token, threads_for_search):
        """Test searching with multiple filters."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get(
            '/api/search/threads?q=JWT&semester=3&courses=cc&subjects=Programação Eficaz',
            headers=headers
        )

        assert response.status_code == 200
        results = response.json['results']

        # All results should match all filters
        for result in results:
            assert result['semester'] == 3
            assert 'cc' in result['courses']
            assert 'Programação Eficaz' in result['subjects']

    def test_search_threads_no_results(self, client, registered_user_token, threads_for_search):
        """Test search with no matching results."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/search/threads?q=xyznonexistent', headers=headers)

        assert response.status_code == 200
        assert response.json['count'] == 0
        assert len(response.json['results']) == 0

    def test_search_threads_missing_query(self, client, registered_user_token):
        """Test search without query parameter."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/search/threads', headers=headers)

        assert response.status_code == 400

    def test_search_threads_unauthorized(self, client, threads_for_search):
        """Test search without authentication."""
        response = client.get('/api/search/threads?q=JWT')
        assert response.status_code == 401

    def test_search_threads_result_structure(self, client, registered_user_token, threads_for_search):
        """Test that search results have correct structure."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/search/threads?q=JWT', headers=headers)

        assert response.status_code == 200
        results = response.json['results']

        if len(results) > 0:
            result = results[0]
            assert 'id' in result
            assert 'title' in result
            assert 'author' in result
            assert 'semester' in result
            assert 'courses' in result
            assert 'subjects' in result
            assert 'score' in result
            assert 'created_at' in result
            assert 'post_count' in result

    def test_search_threads_includes_post_count(self, client, registered_user_token, threads_for_search, post_data):
        """Test that search results include post count."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}

        # Get a thread
        threads_response = client.get('/api/threads', headers=headers)
        thread_id = threads_response.json['threads'][0]['id']

        # Add posts to it
        for i in range(3):
            client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)

        # Search for it
        response = client.get('/api/search/threads?q=a', headers=headers)
        results = response.json['results']

        # Find our thread
        thread_result = next((r for r in results if r['id'] == thread_id), None)
        if thread_result:
            assert thread_result['post_count'] == 3

    def test_search_threads_partial_match(self, client, registered_user_token, threads_for_search):
        """Test that search works with partial matches."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.get('/api/search/threads?q=autent', headers=headers)

        assert response.status_code == 200
        results = response.json['results']

        # Should find threads with "autenticação"
        assert any('autenticação' in r['title'].lower() for r in results)


class TestSearchAndFilterIntegration:
    """Integration tests for search and filters."""

    def test_filter_then_search_workflow(self, client, registered_user_token, threads_for_search):
        """Test typical user workflow: get filters, then search."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}

        # 1. Get filter config
        config_response = client.get('/api/filters/config', headers=headers)
        assert config_response.status_code == 200

        # 2. Get subjects for CC course
        subjects_response = client.get('/api/filters/subjects?courses=cc', headers=headers)
        assert subjects_response.status_code == 200

        # 3. Search with filters
        search_response = client.get(
            '/api/search/threads?q=JWT&courses=cc&semester=3',
            headers=headers
        )
        assert search_response.status_code == 200

    def test_search_respects_thread_filters(self, client, registered_user_token):
        """Test that search respects the same filters as thread list."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}

        # Create threads in different courses
        thread1_data = {
            "title": "Test CC Thread",
            "semester": 3,
            "courses": ["cc"],
            "subjects": ["Programação Eficaz"]
        }
        thread2_data = {
            "title": "Test ADM Thread",
            "semester": 3,
            "courses": ["adm"],
            "subjects": ["Marketing"]
        }

        client.post('/api/threads', json=thread1_data, headers=headers)
        client.post('/api/threads', json=thread2_data, headers=headers)

        # Search with CC filter
        response = client.get('/api/search/threads?q=Test&courses=cc', headers=headers)
        assert response.status_code == 200

        results = response.json['results']
        # Should only get CC thread
        assert all('cc' in r['courses'] for r in results)
