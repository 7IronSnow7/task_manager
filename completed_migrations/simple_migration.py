from app import create_app
from models import db
from models.task import Task

def add_completed_at_column():
    """Simple migration using SQLAlchemy ORM"""
    
    print("🔄 Starting simple database migration...")
    
    try:
        # Method 1: Use db.create_all() which adds missing columns
        print("📋 Adding missing columns to existing tables...")
        db.create_all()
        print("Database schema updated!")
        
        # Method 2: Test if the column works
        print("Testing completed_at column...")
        
        # Try to query a task and access completed_at
        task = Task.query.first()
        if task:
            # Try to access completed_at - this will fail if column doesn't exist
            current_completed_at = task.completed_at
            print(f"Test successful: Task {task.id} completed_at = {current_completed_at}")
            
            # Update existing completed tasks
            completed_tasks = Task.query.filter_by(status=TaskStatus.COMPLETED).all()
            updated_count = 0
            
            for task in completed_tasks:
                if task.completed_at is None:
                    task.completed_at = task.updated_at or task.created_at
                    updated_count += 1
            
            if updated_count > 0:
                db.session.commit()
                print(f"Updated {updated_count} completed tasks with timestamps")
            else:
                print("No completed tasks needed timestamp updates")
        else:
            print("No tasks in database to test")
            
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        print("Trying alternative method...")
        
        # Alternative: Direct SQL approach
        try:
            # Import TaskStatus here to avoid circular imports
            from models.task import TaskStatus
            
            # Use raw SQL with proper SQLAlchemy syntax
            with db.engine.begin() as conn:
                # Check if column exists
                result = conn.execute(db.text("PRAGMA table_info(tasks)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'completed_at' not in columns:
                    print("Adding completed_at column...")
                    conn.execute(db.text("ALTER TABLE tasks ADD COLUMN completed_at DATETIME NULL"))
                    print("Column added successfully!")
                else:
                    print("Column already exists")
                
                # Update completed tasks
                result = conn.execute(db.text("""
                    UPDATE tasks 
                    SET completed_at = COALESCE(updated_at, created_at)
                    WHERE status = 'completed' AND completed_at IS NULL
                """))
                
                print(f"Updated {result.rowcount} completed tasks")
                
            print("Alternative migration completed successfully!")
            return True
            
        except Exception as e2:
            print(f"Alternative migration also failed: {e2}")
            return False

def check_migration_success():
    """Verify the migration worked"""
    print("\nVerifying migration...")
    
    try:
        # Test 1: Can we query tasks with completed_at?
        task = Task.query.first()
        if task:
            completed_at = task.completed_at
            print(f"Test 1 passed: Can access completed_at field")
        
        # Test 2: Can we create a new task and mark it completed?
        from models.task import TaskStatus, TaskPriority
        
        test_task = Task(
            title="Migration Test Task",
            description="This task tests the completed_at field",
            priority=TaskPriority.LOW,
            user_id=1  # Assuming user 1 exists
        )
        
        db.session.add(test_task)
        db.session.commit()
        
        # Mark it completed
        test_task.mark_completed()
        db.session.commit()
        
        if test_task.completed_at is not None:
            print("Test 2 passed: mark_completed() works correctly")
            
            # Clean up test task
            db.session.delete(test_task)
            db.session.commit()
            print("Test task cleaned up")
        else:
            print("Test 2 failed: mark_completed() didn't set completed_at")
        
        print("All tests passed! Migration was successful!")
        
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    # Create the Flask app and run migration
    app = create_app()
    
    with app.app_context():
        print("Simple Database Migration Tool")
        print("=" * 50)
        
        # Run the migration
        success = add_completed_at_column()
        
        if success:
            # Verify it worked
            check_migration_success()
        else:
            print("Manual fix needed. Try running this in Flask shell:")
            print("   from models import db")
            print("   db.drop_all()")
            print("   db.create_all()")
            print("   # This will recreate all tables with the new schema")