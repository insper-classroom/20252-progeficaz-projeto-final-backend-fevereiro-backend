from flask import Blueprint, request, jsonify, current_app
from models import db, Thread, Post

api_bp = Blueprint('api', __name__)


@api_bp.route('/threads', methods=['GET'])
def list_threads():
    threads = Thread.query.order_by(Thread.created_at.desc()).all()
    return jsonify([t.to_dict() for t in threads])


@api_bp.route('/threads', methods=['POST'])
def create_thread():
    data = request.get_json() or {}
    title = data.get('title')
    if not title:
        return jsonify({'error': 'title required'}), 400
    thread = Thread(title=title)
    db.session.add(thread)
    db.session.commit()
    return jsonify(thread.to_dict()), 201


@api_bp.route('/threads/<int:thread_id>', methods=['GET'])
def get_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    posts = [p.to_dict() for p in thread.posts]
    data = thread.to_dict()
    data['posts'] = posts
    return jsonify(data)


@api_bp.route('/threads/<int:thread_id>/posts', methods=['POST'])
def create_post(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    data = request.get_json() or {}
    author = data.get('author') or 'Anonymous'
    content = data.get('content')
    if not content:
        return jsonify({'error': 'content required'}), 400
    post = Post(thread=thread, author=author, content=content)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201
