from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db
from models.task import Task, TaskStatus, TaskPriority
from models.user import User

# Blueprint for task routes
task_bp = Blueprint('tasks', __name__)

@task_bp.route('/')
def index():
    """Display all tasks"""
    tasks = Task.query.all()
    return render_template('tasks/index.html', tasks=tasks)

@task_bp.route('/new', methods=['GET', 'POST'])
def new():
    """Create a new task"""
    if request.method == 'POST':
        # Get from data
         title = request.form.get('title')
         description = request.form.get('description')
         priority = request.form.get('priority', 'medium')
         
         # for now I will be using the first user
         user = User.query.first()
         if not user:
             flash('No user found. Please create a user first.', 'error')
             return redirect(url_for('tasks.index'))
         
         # Create new task
         task = Task(
             title=title,
             description=description,
             priority=TaskPriority(priority),
             user_id=user.id
         )
         
         try:
             db.session.add(task)
             db.session.commit()
             flash('Task created successfully!', 'success')
             return redirect(url_for('tasks.index'))
         except Exception as e:
             db.session.rollback()
             flash(f'Error creating task: {str(e)}', 'error')
             
    return render_template('tasks/new.html')

@task_bp.route('/<int:id>')
def show(id):
    """Show a specific task"""
    task = Task.query.get_or_404(id)
    return render_template('tasks/show.html', task=task)

@task_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit a task"""
    task = Task.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update task with a form data
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = TaskPriority(request.form.get('priority', 'medium'))
        task.status = TaskStatus(request.form.get('status', 'pending'))
        
        try:
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('tasks.show', id=task.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {str(e)}', 'error')
        
    return render_template('tasks/edit.html', task=task)

@task_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a task"""
    task = Task.query.get_or_404(id)
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {str(e)}', 'error')
        
    return redirect(url_for('tasks.index'))

@task_bp.route('/<int:id>/complete', methods=['POST'])
def complete(id):
    """Mark as completed"""
    task = Task.query.get_or_404(id)
    task.mark_completed()
    
    try:
        db.session.commit()
        flash('Task marked as completed!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'error')
        
    return redirect(url_for('tasks.index'))