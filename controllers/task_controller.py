from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.task import Task, TaskStatus, TaskPriority
import pytz

SAST = pytz.timezone('Africa/Johannesburg')
# Blueprint for task routes
task_bp = Blueprint('tasks', __name__)

@task_bp.route('/')
@login_required
def index():
    """Display active tasks (exclude completed tasks)"""
    # Only show pending or in progress tasks here
    active_tasks = Task.query.filter_by(user_id=current_user.id).filter(
        Task.status != TaskStatus.COMPLETED
        ).order_by(Task.created_at.desc()).all()
    
    # Get all tasks for stats
    all_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks/index.html', 
                           tasks=active_tasks,
                           all_tasks=all_tasks)

@task_bp.route('/new')
@login_required
def new():
    """Display a new task form"""
    return render_template('tasks/new.html')

@task_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Handle task creation form submission"""
    # Get from data
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'medium')
    due_date_str = request.form.get('due_date', '')
    
    # Validation
    if not title:
        flash('Task title is required', 'error')
        return redirect(url_for('tasks.new'))
    
    # Parse due date if provided
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            # Check if due date is in the past
            today = date.today()
            if due_date < today:
                flash('Due date cannot be in the past. Please select today or a future date.', 'error')
                return redirect(url_for('tasks.new'))
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('tasks.new'))

    # Create new task
    task = Task(
        title=title,
        description=description,
        priority=TaskPriority(priority),
        user_id=current_user.id,
        due_date=due_date
    )
    
    try:
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating task: {str(e)}', 'error')
        return render_template('tasks/show.html', task=task)

@task_bp.route('/<int:id>')
@login_required
def show(id):
    """Show a specific task (only if it belongs to current user)"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('tasks/show.html', task=task)

@task_bp.route('/<int:id>/edit')
@login_required
def edit(id):
    """Display edit form for a task"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).filter(Task.status != TaskStatus.COMPLETED).first_or_404()
    return render_template('tasks/edit.html', task=task)

@task_bp.route('/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    """Handle task update form submission"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Update task with form data
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'medium')
    status = request.form.get('status', 'pending')
    due_date_str = request.form.get('due_date', '')
    
    # Validation
    if not title:
        flash('Task title is required', 'error')
        return redirect(url_for('tasks.edit', id=task.id))
    
    # Parse due date if provided
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('tasks.edit', id=task.id))
    
    # Update task fields
    task.title = title
    task.description = description
    task.priority = TaskPriority(priority)
    task.status = TaskStatus(status)
    task.due_date = due_date
    task.updated_at = datetime.now(SAST)
    
    try:
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'error')
        
    return render_template('tasks/edit.html', task=task)

@task_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a task (only if it belongs to a current user)"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {str(e)}', 'error')
        
    return redirect(url_for('tasks.index'))

@task_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    """Mark as completed (only if it belongs to current user)"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        task.mark_completed()
        db.session.commit()
        flash('Task marked as completed!', 'success')
        
        # If this is an AJAX request, return JSON response
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'completed': task.status == TaskStatus.COMPLETED
            })
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'error')
        
    return redirect(url_for('tasks.index'))

@task_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_complete(id):
    """Toggle task completion status"""
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if task.status == TaskStatus.COMPLETED:
        flash('Task is already completed and cannot be reopened', 'error')
        return redirect(url_for('tasks.index'))
    
    try:
    # Toggle between completed and pending
        task.mark_completed()
        message = 'Task completed successfully!'
    
        db.session.commit()
        flash(message, 'success')
        
        # If this is an AJAX request, return JSON response
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'completed': task.status == TaskStatus.COMPLETED
            })
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'error')
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'error': str(e)}), 500
        
    return redirect(url_for('tasks.index'))

# Completed tasks sent to a different template
@task_bp.route('/completed')
@login_required
def completed():
    """Display completed tasks categorized by priority"""
    
    # Get all completed tasks for current user
    completed_tasks = Task.query.filter_by(
        user_id=current_user.id,
        status=TaskStatus.COMPLETED
    ).order_by(Task.completed_at.desc()).all()
    
    # Categorize by priority
    high_priority_tasks = [task for task in completed_tasks if task.priority == TaskPriority.HIGH]
    medium_priority_tasks = [task for task in completed_tasks if task.priority == TaskPriority.MEDIUM]
    low_priority_tasks = [task for task in completed_tasks if task.priority == TaskPriority.LOW] 
    
    return render_template('tasks/completed.html',
                           high_priority_tasks=high_priority_tasks,
                           medium_priority_tasks=medium_priority_tasks,
                           low_priority_tasks=low_priority_tasks,
                           total_completed=len(completed_tasks))

# API endpoints for AJAX requests
@task_bp.route('/api/tasks', methods=['GET'])
@login_required
def api_tasks():
    """Get tasks as JSON for AJAX requests"""
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority.value,
            'status': task.status.value,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat() if task.updated_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'is_overdue': task.is_overdue if hasattr(task, 'is_overdue') else False
        })
    
    return jsonify({
        'success': True,
        'tasks': tasks_data,
        'total': len(tasks_data)
    })

@task_bp.route('/api/stats', methods=['GET'])
@login_required
def api_stats():
    """Get task statistics as JSON"""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = len([t for t in tasks if hasattr(t, 'is_overdue') and t.is_overdue and t.status != TaskStatus.COMPLETED])
    
    # Priority breakdown
    high_priority = len([t for t in tasks if t.priority == TaskPriority.HIGH])
    medium_priority = len([t for t in tasks if t.priority == TaskPriority.MEDIUM])
    low_priority = len([t for t in tasks if t.priority == TaskPriority.LOW])
    
    return jsonify({
        'success': True,
        'stats': {
            'total': total_tasks,
            'completed': completed_tasks,
            'pending': pending_tasks,
            'overdue': overdue_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
            'priority_breakdown': {
                'high': high_priority,
                'medium': medium_priority,
                'low': low_priority
            }
        }
    })
    
# Error handlers for this blueprint
@task_bp.errorhandler(404)
def task_not_found(error):
    """Handle 404 errors for tasks"""
    flash('Task not found or you do not have permission to access it.', 'error')
    return redirect(url_for('tasks.index'))

@task_bp.errorhandler(403)
def task_forbidden(error):
    """Handle 403 errors for tasks"""
    flash('You do not have permission to access this task.', 'error')
    return redirect(url_for('tasks.index'))