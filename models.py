from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=True) # Initially nullable for migration
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='World')
    image_url = db.Column(db.String(500), nullable=True)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contributor_name = db.Column(db.String(200), nullable=True)  # For credited user submissions
    attachments = db.relationship('Attachment', backref='post', lazy=True, cascade="all, delete-orphan")

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    is_admin_reply = db.Column(db.Boolean, default=False)
    
    post = db.relationship('Post', backref=db.backref('comments', lazy=True, order_by='Comment.created_at'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facebook_url = db.Column(db.String(500), default='')
    instagram_url = db.Column(db.String(500), default='')
    twitter_url = db.Column(db.String(500), default='')
    whatsapp_url = db.Column(db.String(500), default='')
    youtube_url = db.Column(db.String(500), default='')

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(200), nullable=False)
    author_email = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='World')
    image_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_notes = db.Column(db.Text, nullable=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(200), nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    sex = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(300), nullable=True)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, contacted, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
