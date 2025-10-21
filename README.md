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

4. Edit .env file and set your MONGODB_URI and OPENAI_API_KEY:
   ```
   MONGODB_URI=your_mongodb_connection_string
   OPENAI_API_KEY=your_openai_api_key
   ```

5. Run the app:
   ```bash
   python main.py
   ```

The API will be available at http://localhost:5000/api

## API Endpoints

### Search
- `GET /api/search/threads?q=<query>` - search threads by title
  - Query parameters:
    - `q` (required): search query string
    - `semester` (optional): filter by semester id
    - `courses` (optional): filter by course ids (can be multiple)
    - `subjects` (optional): filter by subject names (can be multiple)
  - Example: `/api/search/threads?q=algoritmo&semester=3&courses=cc`

### Threads
- `GET /api/threads` - list threads
- `POST /api/threads` - create thread `{title, description?}`
  - `description` is optional
- `GET /api/threads/<id>` - get thread with posts
- `PUT /api/threads/<id>` - update thread `{title?, description?}`
  - Both fields are optional, only provided fields will be updated

### Posts
- `GET /api/posts/<id>` - get specific post  
- `POST /api/threads/<id>/posts` - create post `{author, content}`
- `PUT /api/posts/<id>` - update post `{author?, content?}`
  - Both fields are optional, only provided fields will be updated

### Filter Options
- `GET /api/filters/config' - get the complete filter configuration`
- `GET /api/filters/<str:filter_type>' - get the filter configuration for a type`
  - Available types = [semesters, courses, subjects]

### Thread Model
Threads now support an optional `description` field with the following structure:
```json
{
  "id": "thread_id",
  "title": "thread_title",
  "description": "optional_description",  // New field
  "semester": "semester_number",
  "cousers": "[...]", // List of couses from that thread 
  "subjects": "[...]", // List of subjects from that thread 
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

## Content Moderation

The API includes automatic content moderation using OpenAI's moderation API. When creating or updating threads and posts:

- **Threads**: Both title and description are checked for inappropriate content
- **Posts**: Content is checked for inappropriate content

If inappropriate content is detected, the request will be rejected with a 400 status code and a message explaining why the content was blocked. The user's input is preserved on the client side and not deleted.

Categories checked include:
- Sexual content
- Hate speech
- Harassment
- Self-harm content
- Violence
- Threats

Make sure to set your `OPENAI_API_KEY` in the `.env` file for moderation to work.

## Testing
Run the test script to verify the API is working:
```bash
python tests.py
```

## Administration Endpoints

### Health check

- `GET /health - verify if the DB connection`
- `GET /health/detailed - returns a detailed description of DB's health`
