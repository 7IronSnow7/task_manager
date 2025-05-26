from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from config import Config
from models import db
from models.task import Task, TaskPriority, TaskStatus
from models.user import User, create_default_users
from controllers.task_controller import task_bp
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from dotenv import load_dotenv
import os

# Debug .env loading
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"Looking for .env at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

load_dotenv(env_path)  # Force load from specific path

# Debug environment variables
print("DEFAULT_ADMIN_PASSWORD:", os.getenv("DEFAULT_ADMIN_PASSWORD"))
print("DEFAULT_DEMO_PASSWORD:", os.getenv("DEFAULT_DEMO_PASSWORD"))

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
    
    # @app.route('/force-logout')
    # def force_logout():
    #     from flask import logout_user
    #     logout_user()
    #     return redirect(url_for('auth.login'))
    
    
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
        
#     # Register blueprints
#     try:
#         from controllers.task_controller import task_bp
#         app.register_blueprint(task_bp, url_prefix='/tasks')
#         print("Task controller registered successfully!")
#     except Exception as e:
#         print(f"Error registering task controller: {e}")
        
#     @app.route('/routes')
#     def list_routes():
#         routes = []
#         for rule in app.url_map.iter_rules():
#             routes.append(f"{rule.endpoint}: {rule.rule}")
#         return "<br>".join(routes)
    
#     @app.route('/')
#     def hello():
#         return '<h1>Task Manager App is Running!</h1>'
    
#     @app.route('/recreate-db')
#     def recreate_db():
#         db.drop_all()
#         db.create_all()
#         return '<h1>Database Recreated!</h1><p>All tables have been recreated with the latest schema.</p>'
    
#     # Test route to create a task and verify database
#     @app.route('/test')
#     def test_db():
#         from models.user import User
        
#         # Check if test user already exists
#         try:
#             test_user = User.query.filter_by(username="testuser").first()
#             if not test_user:
#                 # Create a test user first
#                 test_user = User(username="testuser", email="test@example.com")
#                 test_user.set_password("password123")
#                 db.session.add(test_user)
#                 db.session.commit()
            
#             return f"<h1>User Test</h1><p>User ID: {test_user.id}</p><p>Username: {test_user.username}</p>"
            
#         except Exception as e:
#             db.session.rollback()
#             return f"<h1>Error:</h1><p>{str(e)}</p>"
        
#     # Separate route to test task creation
#     @app.route('/test-task')
#     def test_task():
#         from models.task import Task, TaskStatus, TaskPriority
#         from models.user import User
        
#         try:
#             # Get the user
#             user = User.query.filter_by(username="testuser").first()
#             if not user:
#                 return "<h1>Error:</h1><p>No user found. Visit /test first</p>"
            
#             # Create task manually with direct assignment
#             task = Task()
#             task.title = "Manual Test Task"
#             task.description = "Testing manual assignment"
#             task.status = TaskStatus.PENDING
#             task.priority = TaskPriority.HIGH
#             task.user_id = user.id  # Direct assignment
            
#             db.session.add(task)
#             db.session.commit()
            
#             return f"<h1>Task Test</h1><p>Task created with user_id: {task.user_id}</p>"
            
#         except Exception as e:
#             db.session.rollback()
#             return f"<h1>Error:</h1><p>{str(e)}</p>"
        
#     return app

# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True)