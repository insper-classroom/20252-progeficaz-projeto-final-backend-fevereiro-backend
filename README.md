# Backend (Flask) for Forum

This is a minimal Flask REST API for the forum application. It uses SQLite by default.

Setup (recommended inside a virtualenv):

1. Install dependencies:

   pip install -r requirements.txt

2. Copy .env.example to .env and adjust if needed.

3. Run the app:

   python app.py

The API will be available at http://localhost:5000/api

Endpoints:
- GET /api/threads - list threads
- POST /api/threads - create thread {title}
- GET /api/threads/<id> - get thread with posts
- POST /api/threads/<id>/posts - create post {author, content}
