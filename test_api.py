import requests
import json

def test_api():
    print("Testing Forum API with Filters...")
    
    try:
        # Test 1: Test root endpoint
        print("\n1. Testing GET /")
        response = requests.get('http://localhost:5000')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Test filter configuration
        print("\n2. Testing GET /api/filters/config")
        response = requests.get('http://localhost:5000/api/filters/config')
        print(f"Status: {response.status_code}")
        config = response.json()
        print(f"Filter config loaded: {list(config.keys())}")
        
        # Test 3: Test semester options
        print("\n3. Testing GET /api/filters/semesters")
        response = requests.get('http://localhost:5000/api/filters/semesters')
        print(f"Status: {response.status_code}")
        semesters = response.json()
        print(f"Semesters available: {len(semesters)}")
        
        # Test 4: Test course options
        print("\n4. Testing GET /api/filters/courses")
        response = requests.get('http://localhost:5000/api/filters/courses')
        print(f"Status: {response.status_code}")
        courses = response.json()
        print(f"Courses available: {len(courses)}")
        
        # Test 5: Test subject options (no filters - should show ALL subjects)
        print("\n5. Testing GET /api/filters/subjects (no filters)")
        response = requests.get('http://localhost:5000/api/filters/subjects')
        print(f"Status: {response.status_code}")
        all_subjects = response.json()
        print(f"All subjects available: {len(all_subjects)}")
        print(f"Sample subjects: {all_subjects[:5] if len(all_subjects) > 5 else all_subjects}")
        
        # Test 6: Test subject options with only semester (should show all subjects for that semester)
        print("\n6. Testing GET /api/filters/subjects?semester=3 (only semester)")
        response = requests.get('http://localhost:5000/api/filters/subjects?semester=3')
        print(f"Status: {response.status_code}")
        semester_subjects = response.json()
        print(f"Subjects for semester 3 (all courses): {len(semester_subjects)}")
        print(f"Semester 3 subjects: {semester_subjects}")
        
        # Test 7: Test subject options with only course (should show all subjects for that course)
        print("\n7. Testing GET /api/filters/subjects?courses=cc (only course)")
        response = requests.get('http://localhost:5000/api/filters/subjects?courses=cc')
        print(f"Status: {response.status_code}")
        course_subjects = response.json()
        print(f"Subjects for Computer Science (all semesters): {len(course_subjects)}")
        print(f"Sample CC subjects: {course_subjects[:10] if len(course_subjects) > 10 else course_subjects}")
        
        # Test 7.1: Test with Administration course only
        print("\n7.1. Testing GET /api/filters/subjects?courses=adm (ADM only)")
        response = requests.get('http://localhost:5000/api/filters/subjects?courses=adm')
        print(f"Status: {response.status_code}")
        adm_subjects = response.json()
        print(f"Subjects for Administration (all semesters): {len(adm_subjects)}")
        print(f"Sample ADM subjects: {adm_subjects[:5] if len(adm_subjects) > 5 else adm_subjects}")
        
        # Test 7.2: Test with multiple courses
        print("\n7.2. Testing GET /api/filters/subjects?courses=cc&courses=adm (multiple courses)")
        response = requests.get('http://localhost:5000/api/filters/subjects?courses=cc&courses=adm')
        print(f"Status: {response.status_code}")
        multi_courses_subjects = response.json()
        print(f"Subjects for CC+ADM (all semesters): {len(multi_courses_subjects)}")
        print(f"Multi-course subjects should include both CC and ADM subjects")
        
        # Test 7.3: Test with non-existent course
        print("\n7.3. Testing GET /api/filters/subjects?courses=nonexistent")
        response = requests.get('http://localhost:5000/api/filters/subjects?courses=nonexistent')
        print(f"Status: {response.status_code}")
        nonexistent_subjects = response.json()
        print(f"Subjects for non-existent course: {len(nonexistent_subjects)}")
        print(f"Should show default subjects: {nonexistent_subjects}")
        
        # Test 8: Test subject options with both course and semester
        print("\n8. Testing GET /api/filters/subjects?courses=cc&semester=3 (both filters)")
        response = requests.get('http://localhost:5000/api/filters/subjects?courses=cc&semester=3')
        print(f"Status: {response.status_code}")
        filtered_subjects = response.json()
        print(f"Subjects for CC semester 3: {len(filtered_subjects)}")
        print(f"CC semester 3 subjects: {filtered_subjects}")
        
        # Test 9: Test subject options with multiple courses and semester
        print("\n9. Testing GET /api/filters/subjects?courses=cc&courses=adm&semester=1")
        response = requests.get('http://localhost:5000/api/filters/subjects?courses=cc&courses=adm&semester=1')
        print(f"Status: {response.status_code}")
        multi_filtered_subjects = response.json()
        print(f"Subjects for CC+ADM semester 1: {len(multi_filtered_subjects)}")
        print(f"Multi-course subjects: {multi_filtered_subjects}")
        
        # Test 10: Test subject search with filters
        print("\n10. Testing GET /api/filters/subjects?q=matematica&semester=1")
        response = requests.get('http://localhost:5000/api/filters/subjects?q=matematica&semester=1')
        print(f"Status: {response.status_code}")
        search_results = response.json()
        print(f"Search 'matematica' in semester 1: {search_results}")
        
        # Test 11: Get all threads (should work even if empty)
        print("\n11. Testing GET /api/threads")
        response = requests.get('http://localhost:5000/api/threads')
        print(f"Status: {response.status_code}")
        threads = response.json()
        print(f"Threads: {len(threads)} found")
        
        # Test 12: Create a new thread with filters
        print("\n12. Testing POST /api/threads (with filters)")
        new_thread = {
            'title': 'Test Thread with Filters',
            'description': 'This is a test thread with filter system',
            'semester': 3,
            'courses': ['cc'],
            'subjects': ['Programação Eficaz', 'Algoritmos e Complexidade']
        }
        response = requests.post('http://localhost:5000/api/threads', json=new_thread)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            thread = response.json()
            thread_id = thread['id']
            print(f"Created thread with ID: {thread_id}")
            print(f"Thread semester: {thread.get('semester')}")
            print(f"Thread courses: {thread.get('courses')}")
            print(f"Thread subjects: {thread.get('subjects')}")
            
            # Test 13: Test thread filtering
            print(f"\n13. Testing GET /api/threads?semester=3")
            response = requests.get('http://localhost:5000/api/threads?semester=3')
            print(f"Status: {response.status_code}")
            filtered_threads = response.json()
            print(f"Threads for semester 3: {len(filtered_threads)}")
            
            # Test 14: Test thread filtering by course
            print(f"\n14. Testing GET /api/threads?courses=cc")
            response = requests.get('http://localhost:5000/api/threads?courses=cc')
            print(f"Status: {response.status_code}")
            filtered_threads = response.json()
            print(f"Threads for Computer Science: {len(filtered_threads)}")
            
            # Test 15: Get the specific thread
            print(f"\n15. Testing GET /api/threads/{thread_id}")
            response = requests.get(f'http://localhost:5000/api/threads/{thread_id}')
            print(f"Status: {response.status_code}")
            thread_detail = response.json()
            print(f"Thread: {thread_detail['title']}")
            print(f"Thread filters - Semester: {thread_detail.get('semester')}, Courses: {thread_detail.get('courses')}, Subjects: {thread_detail.get('subjects')}")
            
            # Test 16: Update thread filters
            print(f"\n16. Testing PUT /api/threads/{thread_id} (update filters)")
            update_data = {
                'semester': 4,
                'courses': ['cc', 'eng_comp'],
                'subjects': ['Sistemas Operacionais', 'Redes de Computadores']
            }
            response = requests.put(f'http://localhost:5000/api/threads/{thread_id}', json=update_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                updated_thread = response.json()
                print(f"Updated filters - Semester: {updated_thread.get('semester')}, Courses: {updated_thread.get('courses')}")
            
            # Test 17: Create a post in the thread
            print(f"\n17. Testing POST /api/threads/{thread_id}/posts")
            new_post = {
                'author': 'Test User',
                'content': 'This is a test post in a filtered thread!'
            }
            response = requests.post(f'http://localhost:5000/api/threads/{thread_id}/posts', json=new_post)
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                post = response.json()
                print(f"Created post by: {post['author']}")
        
        # Test 18: Test creating thread without required filters (should fail)
        print("\n18. Testing POST /api/threads (missing required filters)")
        invalid_thread = {
            'title': 'Invalid Thread',
            'description': 'Missing required filters'
            # Missing semester and subjects
        }
        response = requests.post('http://localhost:5000/api/threads', json=invalid_thread)
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            error = response.json()
            print(f"Expected error: {error.get('error')}")
        
        print("\n✅ API tests with filters completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_api()