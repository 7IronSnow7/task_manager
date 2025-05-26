#!/usr/bin/env python3
"""
Quick script to add sample tasks for testing
Run this after your database is set up
"""

from app import app, db
from models.task import Task
from datetime import datetime, timedelta

def create_sample_tasks():
    """Create sample tasks for testing"""
    
    with app.app_context():
        # First, let's create a test user if User model exists
        from models.user import User
        
        # Check if we have any users, create one if not
        test_user = User.query.first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='dummy_test'
                # Add other required User fields as needed
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ Created test user: {test_user.username}")
        
        # Clear existing tasks (optional)
        # Task.query.delete()
        
        # Sample tasks with different statuses and priorities
        sample_tasks = [
            {
                'title': 'Complete project documentation',
                'description': 'Write comprehensive documentation for the Flask task manager project including setup instructions and API documentation.',
                'priority': 'HIGH',
                'status': 'IN_PROGRESS',
                'due_date': datetime.now().date() + timedelta(days=3)
            },
            {
                'title': 'Review quarterly budget',
                'description': 'Analyze Q4 expenses and prepare budget recommendations for next quarter.',
                'priority': 'MEDIUM',
                'status': 'PENDING',
                'due_date': datetime.now().date() + timedelta(days=7)
            },
            {
                'title': 'Update team presentation',
                'description': 'Revise slides for the monthly team meeting with latest project updates.',
                'priority': 'LOW',
                'status': 'COMPLETED',
                'due_date': datetime.now().date() - timedelta(days=1)
            },
            {
                'title': 'Database optimization',
                'description': 'Optimize database queries and add proper indexes to improve performance.',
                'priority': 'HIGH',
                'status': 'PENDING',
                'due_date': datetime.now().date() + timedelta(days=5)
            },
            {
                'title': 'Code review for feature branch',
                'description': 'Review pull request #42 for the new authentication system.',
                'priority': 'MEDIUM',
                'status': 'IN_PROGRESS',
                'due_date': datetime.now().date() + timedelta(days=1)
            },
            {
                'title': 'Plan team building event',
                'description': 'Organize a fun team building activity for next month.',
                'priority': 'LOW',
                'status': 'PENDING',
                'due_date': datetime.now().date() + timedelta(days=14)
            }
        ]
        
        # Create and add tasks
        for task_data in sample_tasks:
            task = Task(
                title=task_data['title'],
                description=task_data['description'],
                priority=task_data['priority'],
                status=task_data['status'],
                due_date=task_data['due_date'],
                user_id=test_user.id  # Add the user_id here!
            )
            db.session.add(task)
        
        # Commit all tasks
        db.session.commit()
        
        print(f"Successfully created {len(sample_tasks)} sample tasks!")

if __name__ == '__main__':
    create_sample_tasks()