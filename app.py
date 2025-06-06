from controllers.admin_controller import admin_bp
from controllers.auth_controller import auth_bp
from controllers.task_controller import task_bp
from config import Config
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from models import db
from models.task import Task, TaskPriority, TaskStatus
from models.user import User, create_default_users

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Setup flask login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add hasattr and temoplate filters    
    app.jinja_env.globals['hasattr'] = hasattr
    app.jinja_env.globals['TaskStatus'] = TaskStatus
    app.jinja_env.globals['TaskPriority'] = TaskPriority
    
    
    # Template filters for enums
    @app.template_filter('enum_name')
    def enum_name(value):
        if hasattr(value, 'name'):
            return value.name
        return str(value).upper()
    
    @app.template_filter('enum_display')
    def enum_display(value):
        if hasattr(value, 'name'):
            return value.name.replace('_', ' ').title()
        return str(value).replace('_', ' ').title()
    
    @app.template_filter('priority_class')
    def priority_class(priority):
        priority_name = priority.name if hasattr(priority, 'name') else str(priority).upper()
        if priority_name == 'HIGH':
            return 'border-red-500'
        elif priority_name == 'MEDIUM':
            return 'border-yellow-500'
        elif priority_name == 'LOW':
            return 'border-blue-500'
        return 'border-gray-500'
    
    @app.template_filter('status_class')
    def status_class(status):
        status_name = status.name if hasattr(status, 'name') else str(status).upper()
        if status_name == 'COMPLETED':
            return 'border-green-500'
        elif status_name == 'IN_PROGRESS':
            return 'border-yellow-500'
        elif status_name == 'TODO':
            return 'border-gray-400'
        return 'border-gray-300'
    
    # Register blueprints    
    app.register_blueprint(task_bp, url_prefix='/tasks')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Home route  redirect to tasks and login
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('tasks.index'))
        return redirect(url_for('auth.login'))
    
    # Create database tables and default users
    with app.app_context():
        db.create_all()
        create_default_users()
        
    return app

app = create_app()
if __name__ == '__main__':
    app.run(debug=True)