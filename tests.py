import requests
import json
from dotenv import load_dotenv
# Load environment variables
load_dotenv(".env")

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
        
        # Test 2.1: Test creating thread without authentication (should fail)
        print("\n2.1. Testing POST /api/threads without authentication")
        test_thread = {
            'title': 'Unauthorized Test Thread',
            'description': 'This should fail'
        }
        response = requests.post('http://localhost:5000/api/threads', json=test_thread)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication for thread creation")
        else:
            print(f"❌ Expected 401 (unauthorized), got {response.status_code}")
        
        # Test 2.5: Setup authentication for subsequent tests
        print("\n2.5. Setting up authentication")
        test_user = {
            'email': 'testuser@al.insper.edu.br',
            'password': 'testpass123'
        }
        
        # Try to register user (might already exist)
        response = requests.post('http://localhost:5000/api/auth/register', json=test_user)
        print(f"Registration attempt - Status: {response.status_code}")
        
        # Login to get token
        response = requests.post('http://localhost:5000/api/auth/login', json=test_user)
        print(f"Login - Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Authentication failed. Cannot proceed with tests that require authentication.")
            return
        
        token_data = response.json()
        token = token_data.get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Authentication successful")
        
        # Test 2.6: Test getting current user info
        print("\n2.6. Testing GET /api/auth/me")
        response = requests.get('http://localhost:5000/api/auth/me', headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"User info: username={user_info.get('username')}, email={user_info.get('email')}")
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
        
        # Test 3: Create a new thread (now with authentication)
        print("\n3. Testing POST /api/threads (authenticated)")
        new_thread = {
            'title': 'Test Thread from API',
            'description': 'This is a test thread description'
        }
        response = requests.post('http://localhost:5000/api/threads', json=new_thread, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            thread = response.json()
            thread_id = thread['id']
            print(f"Created thread with ID: {thread_id}")
            print(f"Thread description: {thread.get('description', 'No description')}")
            
            # Test 4: Get the specific thread
            print(f"\n4. Testing GET /api/threads/{thread_id}")
            response = requests.get(f'http://localhost:5000/api/threads/{thread_id}')
            print(f"Status: {response.status_code}")
            thread_detail = response.json()
            print(f"Thread: {thread_detail['title']}")
            print(f"Thread description: {thread_detail.get('description', 'No description')}")
            print(f"Posts: {len(thread_detail.get('posts', []))}")
            
            # Test 4.5: Update the thread description
            print(f"\n4.5. Testing PUT /api/threads/{thread_id}")
            update_thread_data = {
                'description': 'Updated thread description from API test'
            }
            response = requests.put(f'http://localhost:5000/api/threads/{thread_id}', json=update_thread_data, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                updated_thread = response.json()
                print(f"Updated thread description: {updated_thread.get('description', 'No description')}")
            
            # Test 5: Create a post in the thread (now with authentication)
            print(f"\n5. Testing POST /api/threads/{thread_id}/posts")
            new_post = {
                'content': 'This is a test post from the API!'
            }
            response = requests.post(f'http://localhost:5000/api/threads/{thread_id}/posts', json=new_post, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                post = response.json()
                post_id = post['id']
                print(f"Created post by: {post['author']}")
                
                # Test 6: Update the post content
                print(f"\n6. Testing PUT /api/posts/{post_id}")
                update_data = {
                    'content': 'Updated content for the test post'
                }
                response = requests.put(f'http://localhost:5000/api/posts/{post_id}', json=update_data, headers=headers)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    updated_post = response.json()
                    print(f"Updated content: {updated_post.get('content', 'No content')}")
                
                # Test 7: Get the thread again to see the post
                print(f"\n7. Testing GET /api/threads/{thread_id} (with post)")
                response = requests.get(f'http://localhost:5000/api/threads/{thread_id}')
                thread_detail = response.json()
                print(f"Posts: {len(thread_detail.get('posts', []))}")
                if thread_detail.get('posts'):
                    latest_post = thread_detail['posts'][-1]
                    print(f"Latest post: {latest_post['content']}")
                    
                # Test 8: Get specific post
                print(f"\n8. Testing GET /api/posts/{post_id}")
                response = requests.get(f'http://localhost:5000/api/posts/{post_id}')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    post_detail = response.json()
                    print(f"Post content: {post_detail['content']}")
                    print(f"Post author: {post_detail['author']}")
                    print(f"Post upvotes: {post_detail.get('upvotes', 0)}")
                    print(f"Post downvotes: {post_detail.get('downvotes', 0)}")
                    print(f"Post score: {post_detail.get('score', 0)}")
                
                # Test 9: Test voting (requires authentication)
                print(f"\n9. Testing voting without authentication")
                response = requests.post(f'http://localhost:5000/api/posts/{post_id}/upvote')
                print(f"Upvote without auth - Status: {response.status_code}")
                if response.status_code == 401:
                    print("✅ Correctly requires authentication for voting")
                
                # Test 10: Test upvoting with authentication
                print(f"\n10. Testing authenticated upvoting")
                response = requests.post(f'http://localhost:5000/api/posts/{post_id}/upvote', headers=headers)
                print(f"Upvote - Status: {response.status_code}")
                if response.status_code == 201:
                    vote_result = response.json()
                    print(f"Upvotes: {vote_result.get('upvotes', 0)}")
                    print(f"Score: {vote_result.get('score', 0)}")
                
                # Test 11: Test duplicate upvote (should fail - one vote per user)
                print(f"\n11. Testing duplicate upvote")
                response = requests.post(f'http://localhost:5000/api/posts/{post_id}/upvote', headers=headers)
                print(f"Duplicate upvote - Status: {response.status_code}")
                if response.status_code == 409:
                    print("✅ Correctly prevents duplicate voting")
                else:
                    print(f"❌ Expected 409, got {response.status_code}: {response.json()}")
                
                # Test 12: Test downvoting (should fail since user already voted)
                print(f"\n12. Testing downvote after upvote")
                response = requests.post(f'http://localhost:5000/api/posts/{post_id}/downvote', headers=headers)
                print(f"Downvote - Status: {response.status_code}")
                if response.status_code == 409:
                    print("✅ Correctly prevents second vote from same user")
                else:
                    vote_result = response.json()
                    print(f"Upvotes: {vote_result.get('upvotes', 0)}")
                    print(f"Downvotes: {vote_result.get('downvotes', 0)}")
                    print(f"Score: {vote_result.get('score', 0)}")
                
                # Test 13: Test removing vote
                print(f"\n13. Testing vote removal")
                response = requests.delete(f'http://localhost:5000/api/posts/{post_id}/vote', headers=headers)
                print(f"Remove vote - Status: {response.status_code}")
                if response.status_code == 200:
                    vote_result = response.json()
                    print(f"After removal upvotes: {vote_result.get('upvotes', 0)}")
                    print(f"After removal downvotes: {vote_result.get('downvotes', 0)}")
                    print(f"After removal score: {vote_result.get('score', 0)}")
                
                # Test 14: Test voting again after removal
                print(f"\n14. Testing downvote after vote removal")
                response = requests.post(f'http://localhost:5000/api/posts/{post_id}/downvote', headers=headers)
                print(f"Downvote after removal - Status: {response.status_code}")
                if response.status_code == 201:
                    vote_result = response.json()
                    print(f"✅ Can vote again after removal")
                    print(f"Final upvotes: {vote_result.get('upvotes', 0)}")
                    print(f"Final downvotes: {vote_result.get('downvotes', 0)}")
                    print(f"Final score: {vote_result.get('score', 0)}")
                
                # Test 15: Test thread upvoting with authentication
                print(f"\n15. Testing authenticated thread upvoting")
                response = requests.post(f'http://localhost:5000/api/threads/{thread_id}/upvote', headers=headers)
                print(f"Thread upvote - Status: {response.status_code}")
                if response.status_code == 201:
                    vote_result = response.json()
                    print(f"Thread upvotes: {vote_result.get('upvotes', 0)}")
                    print(f"Thread score: {vote_result.get('score', 0)}")
                
                # Test 16: Test duplicate thread upvote (should fail - one vote per user)
                print(f"\n16. Testing duplicate thread upvote")
                response = requests.post(f'http://localhost:5000/api/threads/{thread_id}/upvote', headers=headers)
                print(f"Duplicate thread upvote - Status: {response.status_code}")
                if response.status_code == 409:
                    print("✅ Correctly prevents duplicate thread voting")
                else:
                    print(f"❌ Expected 409, got {response.status_code}: {response.json()}")
                
                # Test 17: Test thread downvoting (should fail since user already voted)
                print(f"\n17. Testing thread downvote after upvote")
                response = requests.post(f'http://localhost:5000/api/threads/{thread_id}/downvote', headers=headers)
                print(f"Thread downvote - Status: {response.status_code}")
                if response.status_code == 409:
                    print("✅ Correctly prevents second vote from same user on thread")
                else:
                    vote_result = response.json()
                    print(f"Thread upvotes: {vote_result.get('upvotes', 0)}")
                    print(f"Thread downvotes: {vote_result.get('downvotes', 0)}")
                    print(f"Thread score: {vote_result.get('score', 0)}")
                
                # Test 18: Test removing thread vote
                print(f"\n18. Testing thread vote removal")
                response = requests.delete(f'http://localhost:5000/api/threads/{thread_id}/vote', headers=headers)
                print(f"Remove thread vote - Status: {response.status_code}")
                if response.status_code == 200:
                    vote_result = response.json()
                    print(f"After removal thread upvotes: {vote_result.get('upvotes', 0)}")
                    print(f"After removal thread downvotes: {vote_result.get('downvotes', 0)}")
                    print(f"After removal thread score: {vote_result.get('score', 0)}")
                
                # Test 19: Test thread voting again after removal
                print(f"\n19. Testing thread downvote after vote removal")
                response = requests.post(f'http://localhost:5000/api/threads/{thread_id}/downvote', headers=headers)
                print(f"Thread downvote after removal - Status: {response.status_code}")
                if response.status_code == 201:
                    vote_result = response.json()
                    print(f"✅ Can vote on thread again after removal")
                    print(f"Final thread upvotes: {vote_result.get('upvotes', 0)}")
                    print(f"Final thread downvotes: {vote_result.get('downvotes', 0)}")
                    print(f"Final thread score: {vote_result.get('score', 0)}")
        
        print("\n✅ API tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_api()