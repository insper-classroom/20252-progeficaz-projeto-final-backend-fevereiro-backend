# Backend (Flask) for Forum

This is a minimal Flask REST API for the forum application. It uses MongoDB as the database.

## Setup

### Prerequisites
- Python 3.7+
- MongoDB (either local installation or MongoDB Atlas cloud)

### Database Setup

#### Option 1: Local MongoDB
1. Install MongoDB from https://www.mongodb.com/try/download/community
2. Start MongoDB service
3. The default connection string `mongodb://localhost:27017/forum_db` will work

#### Option 2: MongoDB Atlas (Cloud)
1. Create a free account at https://www.mongodb.com/atlas
2. Create a cluster and get your connection string
3. Update the MONGODB_URI in your .env file

### Application Setup

1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy .env.example to .env and configure your MongoDB connection:
   ```bash
   copy .env.example .env  # On Windows
   # cp .env.example .env  # On macOS/Linux
   ```

4. Edit .env file and set your MONGODB_URI if needed

5. Run the app:
   ```bash
   python app.py
   ```

The API will be available at http://localhost:5000/api

## API Endpoints

### Threads
- `GET /api/threads` - list threads
- `POST /api/threads` - create thread `{title, description?}`
  - `description` is optional
- `GET /api/threads/<id>` - get thread with posts
- `PUT /api/threads/<id>` - update thread `{title?, description?}`
  - Both fields are optional, only provided fields will be updated

### Posts
- `POST /api/threads/<id>/posts` - create post `{author, content}`
- `GET /api/posts/<id>` - get specific post  
- `PUT /api/posts/<id>` - update post `{author?, content?}`
  - Both fields are optional, only provided fields will be updated

### Thread Model
Threads now support an optional `description` field with the following structure:
```json
{
  "id": "thread_id",
  "title": "thread_title",
  "description": "optional_description",  // New field
  "created_at": "2025-01-01T00:00:00.000000",
  "posts": [...] // Only included in GET /api/threads/<id>
}
```

### Post Model
Posts have the following structure:
```json
{
  "id": "post_id",
  "thread_id": "thread_id", 
  "author": "author_name",
  "content": "post_content",
  "created_at": "2025-01-01T00:00:00.000000"
}
```

## Testing
Run the test script to verify the API is working:
```bash
python test_api.py
```
