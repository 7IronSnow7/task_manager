from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from . import db
from dotenv import load_dotenv
import os

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User details
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    
    # Relationships with tasks
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.id}, username = {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return{
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'task_count': len(self.tasks)
        }
        
    @classmethod
    def find_by_username(cls, username):
        """Find user by name"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()
    
def create_default_users():
    """Default users for demo/development if they don't exist"""
    default_users = [
        {
            "username": "admin",
            "email": "admin@taskmanager.com",
            "password": os.getenv("DEFAULT_ADMIN_PASSWORD", "taskmanager123")
        },
        {
            "username": "demo",
            "email": "demo@taskmanager.com",
            "password": os.getenv("DEFAULT_DEMO_PASSWORD", "demo123")
        }
    ]
    
    for user_data in default_users:
        if not User.find_by_username(user_data["username"]):
            new_user = User()
            new_user.username = user_data["username"]
            new_user.email = user_data["email"]
            new_user.set_password(user_data["password"]) # This will hash the password
            db.session.add(new_user)
            print(f"Creating user: {user_data['username']} with password: {user_data['password']}")
    
    try:
        db.session.commit()
        print("Default users created")
    except Exception as e:
        db.session.rollback()
        print(f"Error {str(e)}")