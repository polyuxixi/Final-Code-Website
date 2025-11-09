from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
import jwt
import os
import json
import threading
import time
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-horror')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ai_urban_legends.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default='👻')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='author', lazy=True)
    
class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='urban')
    location = db.Column(db.String(100))
    is_ai_generated = db.Column(db.Boolean, default=False)
    ai_persona = db.Column(db.String(100))
    current_state = db.Column(db.String(50), default='init')
    state_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='story', lazy=True, cascade='all, delete-orphan')
    evidence = db.relationship('Evidence', backref='story', lazy=True, cascade='all, delete-orphan')
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_ai_response = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    evidence_type = db.Column(db.String(20))
    file_path = db.Column(db.String(500))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'story_id', name='_user_story_uc'),)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    notification_type = db.Column(db.String(50), nullable=False) # e.g., 'new_reply', 'story_update'
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/generated', exist_ok=True)
    os.makedirs('static/evidence', exist_ok=True)

def generate_token(user_id):
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        data = jwt.decode(token.replace('Bearer ', ''), app.config['SECRET_KEY'], algorithms=['HS256'])
        return data['user_id']
    except:
        return None

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    
    db.session.add(user)
    db.session.commit()
    
    token = generate_token(user.id)
    
    return jsonify({
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'avatar': user.avatar}
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = generate_token(user.id)
    
    return jsonify({
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'avatar': user.avatar}
    })

@app.route('/api/generate_story', methods=['POST'])
def generate_new_story():
    """Generate a new AI story on demand"""
    try:
        from ai_engine import generate_ai_story_with_meta, generate_evidence_image
        from story_engine import initialize_story_state
        from datetime import datetime, timedelta
        
        # Generate new story
        story_data = generate_ai_story_with_meta()
        
        if not story_data:
            return jsonify({'error': 'Failed to generate story'}), 500
        
        # Create story in database
        new_story = Story(
            title=story_data['title'],
            content=story_data['content'],
            category=story_data['category'],
            location=story_data['location'],
            is_ai_generated=True,
            ai_persona=story_data['ai_persona']
        )
        
        # Initialize state machine
        new_story = initialize_story_state(new_story)
        
        db.session.add(new_story)
        db.session.flush()  # 获取story ID
        
        # 自动生成证据图片
        try:
            evidence_paths = generate_evidence_image(
                story_data['title'], 
                story_data['content'],
                story_data['category']
            )
            
            # 创建证据记录
            evidence_descriptions = [
                '【现场拍摄】刚才偷偷拍的，手有点抖。大家看出什么问题了吗？（手机拍摄，画质一般）',
                '【证据照片】放大后能看到一些细节...我不知道该怎么解释这个。（iPhone夜间模式）',
                '【更新】找到了之前拍的照片，上传给大家看看。注意看背景那里。（旧照片翻拍）',
                '【局部特写】用手机放大拍的，不是很清楚但能看出个大概。（手机变焦拍摄）',
                '【诡异】这张是什么情况？我发誓拍的时候没看到这个...（低光模式，有噪点）'
            ]
            
            for idx, evidence_path in enumerate(evidence_paths):
                evidence = Evidence(
                    story_id=new_story.id,
                    evidence_type='image',
                    file_path=evidence_path,
                    description=evidence_descriptions[idx % len(evidence_descriptions)],
                    created_at=datetime.utcnow() - timedelta(minutes=random.randint(10, 120))
                )
                db.session.add(evidence)
            
            print(f"✅ 为新故事创建了 {len(evidence_paths)} 个证据项")
        except Exception as e:
            print(f"⚠️ 生成证据图片失败: {e}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'story': {
                'id': new_story.id,
                'title': new_story.title,
                'content': new_story.content[:200] + '...' if len(new_story.content) > 200 else new_story.content,
                'category': new_story.category,
                'location': new_story.location,
                'is_ai_generated': new_story.is_ai_generated,
                'ai_persona': new_story.ai_persona,
                'current_state': new_story.current_state,
                'created_at': new_story.created_at.isoformat(),
                'views': new_story.views,
                'post_ip': story_data.get('post_ip', ''),
                'post_time': story_data.get('post_time', '')
            }
        })
        
    except Exception as e:
        print(f"Error in generate_new_story: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stories', methods=['GET'])
def get_stories():
    stories = Story.query.order_by(Story.created_at.desc()).all()
    
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'content': s.content[:200] + '...' if len(s.content) > 200 else s.content,
        'category': s.category,
        'location': s.location,
        'is_ai_generated': s.is_ai_generated,
        'ai_persona': s.ai_persona,
        'current_state': s.current_state,
        'created_at': s.created_at.isoformat(),
        'views': s.views,
        'comments_count': len(s.comments),
        'evidence_count': len(s.evidence)
    } for s in stories])

@app.route('/api/stories/<int:story_id>', methods=['GET'])
def get_story(story_id):
    story = Story.query.get_or_404(story_id)
    story.views += 1
    db.session.commit()
    
    return jsonify({
        'id': story.id,
        'title': story.title,
        'content': story.content,
        'category': story.category,
        'location': story.location,
        'is_ai_generated': story.is_ai_generated,
        'ai_persona': story.ai_persona,
        'current_state': story.current_state,
        'created_at': story.created_at.isoformat(),
        'views': story.views,
        'evidence': [{
            'id': e.id,
            'type': e.evidence_type,
            'file_path': e.file_path,
            'description': e.description,
            'created_at': e.created_at.isoformat()
        } for e in story.evidence],
        'comments': [{
            'id': c.id,
            'content': c.content,
            'is_ai_response': c.is_ai_response,
            'author': {
                'id': c.author.id if c.author else None,
                'username': c.author.username if c.author else 'AI',
                'avatar': c.author.avatar if c.author else '🤖'
            },
            'created_at': c.created_at.isoformat()
        } for c in story.comments]
    })

@app.route('/api/stories/<int:story_id>/comments', methods=['POST'])
def add_comment(story_id):
    token = request.headers.get('Authorization')
    user_id = verify_token(token) if token else None
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    story = Story.query.get_or_404(story_id)
    
    comment = Comment(
        content=data.get('content'),
        story_id=story_id,
        author_id=user_id,
        is_ai_response=False
    )
    
    db.session.add(comment)
    
    # Record user interaction for state machine
    from story_engine import record_user_interaction
    record_user_interaction(story)
    
    db.session.commit()
    
    # Create notification for user's own comment (for AI response)
    create_notifications_for_followers(story, comment)

    # 启动后台线程，5秒后生成AI回复（测试用）
    print(f"[add_comment] 启动后台线程，5秒后生成AI回复...")
    threading.Thread(
        target=delayed_ai_response,
        args=(story_id, comment.id, 5),  # 5秒延迟（测试）
        daemon=True
    ).start()
    
    return jsonify({
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': {
                'id': comment.author.id,
                'username': comment.author.username,
                'avatar': comment.author.avatar
            },
            'created_at': comment.created_at.isoformat()
        },
        'ai_response_pending': True,
        'message': 'AI楼主正在思考回复，请稍候...'
    }), 201

@app.route('/api/stories/<int:story_id>/follow', methods=['POST', 'GET'])
def follow_story(story_id):
    token = request.headers.get('Authorization')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    story = Story.query.get_or_404(story_id)
    follow = Follow.query.filter_by(user_id=user_id, story_id=story_id).first()

    if request.method == 'GET':
        return jsonify({'followed': bool(follow)})

    if follow:
        db.session.delete(follow)
        db.session.commit()
        return jsonify({'status': 'unfollowed'})
    else:
        new_follow = Follow(user_id=user_id, story_id=story_id)
        db.session.add(new_follow)
        db.session.commit()
        return jsonify({'status': 'followed'})

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    token = request.headers.get('Authorization')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    
    return jsonify([{
        'id': n.id,
        'content': n.content,
        'story_id': n.story_id,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications])

@app.route('/api/notifications/read', methods=['POST'])
def read_notifications():
    token = request.headers.get('Authorization')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    notification_ids = data.get('ids', [])

    Notification.query.filter(
        Notification.user_id == user_id,
        Notification.id.in_(notification_ids)
    ).update({'is_read': True}, synchronize_session=False)
    
    db.session.commit()
    return jsonify({'status': 'success'})

def create_notifications_for_followers(story, comment, ai_response=False):
    with app.app_context():
        followers = Follow.query.filter_by(story_id=story.id).all()
        for follow in followers:
            # Don't notify the user who made the comment
            if not ai_response and follow.user_id == comment.author_id:
                continue

            notification = Notification(
                user_id=follow.user_id,
                story_id=story.id,
                comment_id=comment.id,
                notification_type='new_reply' if not ai_response else 'story_update',
                content=f'你关注的故事 "{story.title}" 有了新回复。' if not ai_response else f'你关注的故事 "{story.title}" 有了新进展。'
            )
            db.session.add(notification)
        db.session.commit()

def delayed_ai_response(story_id, comment_id, delay_seconds=60):
    """延迟生成AI回复"""
    print(f"[delayed_ai_response] 开始等待 {delay_seconds} 秒... story_id={story_id}, comment_id={comment_id}")
    time.sleep(delay_seconds)
    
    print(f"[delayed_ai_response] 开始生成AI回复...")
    with app.app_context():
        story = Story.query.get(story_id)
        comment = Comment.query.get(comment_id)
        
        if not story or not comment:
            print(f"[delayed_ai_response] ERROR: Story or Comment not found!")
            return
        
        print(f"[delayed_ai_response] 调用 generate_ai_response...")
        from ai_engine import generate_ai_response
        ai_response = generate_ai_response(story, comment)
        print(f"[delayed_ai_response] AI回复生成完成: {ai_response[:50]}..." if ai_response else "[delayed_ai_response] AI回复为空!")
        
        if ai_response:
            ai_comment = Comment(
                content=ai_response,
                story_id=story_id,
                author_id=None,
                is_ai_response=True
            )
            db.session.add(ai_comment)
            db.session.commit()
            
            # 创建通知给评论者
            notification = Notification(
                user_id=comment.author_id,
                story_id=story_id,
                comment_id=ai_comment.id,
                notification_type='ai_reply',
                content=f'AI楼主回复了你在 "{story.title}" 中的评论。'
            )
            db.session.add(notification)
            
            # 通知所有关注者
            create_notifications_for_followers(story, ai_comment, ai_response=True)
            
            db.session.commit()

if __name__ == '__main__':
    # Start background scheduler for AI story generation
    from scheduler_tasks import start_scheduler
    scheduler = start_scheduler(app)
    
    try:
        app.run(debug=True, port=5001)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
