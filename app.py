from flask import Flask
from config import Config
from models import db
from models.task import Task, TaskPriority, TaskStatus
from models.user import User
from controllers.task_controller import task_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    app.jinja_env.globals['hasattr'] = hasattr
    app.register_blueprint(task_bp, url_prefix='/tasks')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
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