import os
from pathlib import Path

basedir = Path(__file__).parent
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-please'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{basedir / "task_manager.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False