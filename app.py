from flask import Flask
from config import Config
from models import db
from models.task import Task
from models.user import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def hello():
        return '<h1>Task Manager App is Running!</h1>'
    
    @app.route('/recreate-db')
    def recreate_db():
        db.drop_all()
        db.create_all()
        return '<h1>Database Recreated!</h1><p>All tables have been recreated with the latest schema.</p>'
    
    # Test route to create a task and verify database
    @app.route('/test')
    def test_db():
        from models.user import User
        
        # Check if test user already exists
        try:
            test_user = User.query.filter_by(username="testuser").first()
            if not test_user:
                # Create a test user first
                test_user = User(username="testuser", email="test@example.com")
                test_user.set_password("password123")
                db.session.add(test_user)
                db.session.commit()
            
            return f"<h1>User Test</h1><p>User ID: {test_user.id}</p><p>Username: {test_user.username}</p>"
            
            # # Step 2: Verify user was created and get ID
            # user_id = test_user.id
            # print(f"Created user with ID: {user_id}")
            
            # # Step 3: Create task with explicit user_id
            # # Create a task user with the user_id
            # test_task = Task(
            #     title="Test Task",
            #     description="This is a test task to verify database works",
            #     status=TaskStatus.PENDING,
            #     priority=TaskPriority.HIGH
            # )
        
            # db.session.add(test_task)
            # db.session.commit()
            
            # return f"<h1>Success!</h1><p>User ID: {user_id}</p><p>Task created successfully!</p>"

        except Exception as e:
            db.session.rollback()
            return f"<h1>Error:</h1><p>{str(e)}</p>"
        
        # # Get all tasks and users
        # users = User.query.all()
        # tasks = Task.query.all()
        
        # output = "<h1>Database Contents</h1>"
        # output += f"<h2>Users ({len(users)}):</h2><ul>"
        # for user in users:
        #     output += f"<li>ID: {user.id}, Username: {user.username}, Email: {user.email}</li>"
        # output += "</ul>"
        
        # output += f"<h2>Tasks ({len(tasks)}):</h2><ul>"
        # for task in tasks:
        #     output += f"<li>ID: {task.id}, Title: {task.title}, User ID: {task.user_id}, Status: {task.status.value}</li>"
        # output += "</ul>"
        
        # return output
    
    # Separate route to test task creation
    @app.route('/test-task')
    def test_task():
        from models.task import Task, TaskStatus, TaskPriority
        from models.user import User
        
        try:
            # Get the user
            user = User.query.filter_by(username="testuser").first()
            if not user:
                return "<h1>Error:</h1><p>No user found. Visit /test first</p>"
            
            # Create task manually with direct assignment
            task = Task()
            task.title = "Manual Test Task"
            task.description = "Testing manual assignment"
            task.status = TaskStatus.PENDING
            task.priority = TaskPriority.HIGH
            task.user_id = user.id  # Direct assignment
            
            db.session.add(task)
            db.session.commit()
            
            return f"<h1>Task Test</h1><p>Task created with user_id: {task.user_id}</p>"
            
        except Exception as e:
            db.session.rollback()
            return f"<h1>Error:</h1><p>{str(e)}</p>"
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)