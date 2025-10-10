import requests
import json

def test_api():
    print("Testing Forum API...")
    
    try:
        # Test 1: Test root endpoint
        print("\n1. Testing GET /")
        response = requests.get('http://localhost:5000')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Get all threads (should work even if empty)
        print("\n2. Testing GET /api/threads")
        response = requests.get('http://localhost:5000/api/threads')
        print(f"Status: {response.status_code}")
        threads = response.json()
        print(f"Threads: {len(threads)} found")
        
        # Test 3: Create a new thread
        print("\n3. Testing POST /api/threads")
        new_thread = {'title': 'Test Thread from API'}
        response = requests.post('http://localhost:5000/api/threads', json=new_thread)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            thread = response.json()
            thread_id = thread['id']
            print(f"Created thread with ID: {thread_id}")
            
            # Test 4: Get the specific thread
            print(f"\n4. Testing GET /api/threads/{thread_id}")
            response = requests.get(f'http://localhost:5000/api/threads/{thread_id}')
            print(f"Status: {response.status_code}")
            thread_detail = response.json()
            print(f"Thread: {thread_detail['title']}")
            print(f"Posts: {len(thread_detail.get('posts', []))}")
            
            # Test 5: Create a post in the thread
            print(f"\n5. Testing POST /api/threads/{thread_id}/posts")
            new_post = {
                'author': 'Test User',
                'content': 'This is a test post from the API!'
            }
            response = requests.post(f'http://localhost:5000/api/threads/{thread_id}/posts', json=new_post)
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                post = response.json()
                print(f"Created post by: {post['author']}")
                
                # Test 6: Get the thread again to see the post
                print(f"\n6. Testing GET /api/threads/{thread_id} (with post)")
                response = requests.get(f'http://localhost:5000/api/threads/{thread_id}')
                thread_detail = response.json()
                print(f"Posts: {len(thread_detail.get('posts', []))}")
                if thread_detail.get('posts'):
                    print(f"Latest post: {thread_detail['posts'][-1]['content']}")
        
        print("\n✅ API tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_api()