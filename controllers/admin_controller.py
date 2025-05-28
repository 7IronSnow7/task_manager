from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models.user import User
from models.task import Task, TaskStatus, TaskPriority
from models import db
from datetime import datetime, timedelta
from sqlalchemy import func

# Create blueprint
admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    
    # Get basic stats
    total_users = User.query.count()
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status=TaskStatus.COMPLETED).count()
    pending_tasks = Task.query.filter(Task.status != TaskStatus.COMPLETED).count()
    
    # Get recent users (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_users = User.query.filter(User.created_at >= week_ago).count()
    
    # Get task statistics by priority
    high_priority_tasks = Task.query.filter_by(priority=TaskPriority.HIGH).count()
    medium_priority_tasks = Task.query.filter_by(priority=TaskPriority.MEDIUM).count()
    low_priority_tasks = Task.query.filter_by(priority=TaskPriority.LOW).count()
    
    # Get recent tasks
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(10).all()
    
    # Get user activity (users with most tasks)
    user_activity = db.session.query(
        User.username,
        User.email,
        func.count(Task.id).label('task_count')
    ).outerjoin(Task).group_by(User.id).order_by(func.count(Task.id).desc()).all()
    
    stats = {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'recent_users': recent_users,
        'high_priority_tasks': high_priority_tasks,
        'medium_priority_tasks': medium_priority_tasks,
        'low_priority_tasks': low_priority_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_tasks=recent_tasks,
                         user_activity=user_activity)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Display all users for user management"""
    users = User.query.order_by(User.created_at.desc()).all()
    
    user_data = []
    for user in users:
        # Get task statistcis for each user
        total_tasks = Task.query.filter_by(user_id=user.id).count()
        completed_tasks = Task.query.filter_by(user_id=user.id, status=TaskStatus.COMPLETED).count()
        pending_tasks = total_tasks - completed_tasks
        
        user_data.append({
            'user':user,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks
        })
    return render_template('admin/manage_users.html', user_data=user_data)

@admin_bp.route('/tasks')
@login_required
@admin_required
def tasks():
    """View all tasks"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    user_filter = request.args.get('user_id')
    
    # Build query
    query = Task.query
    
    if status_filter:
        query = query.filter_by(status=TaskStatus(status_filter))
    if priority_filter:
        query = query.filter_by(priority=TaskPriority(priority_filter))
    if user_filter:
        query = query.filter_by(user_id=user_filter)
    
    tasks_pagination = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get all users for filter dropdown
    all_users = User.query.order_by(User.username).all()
    
    return render_template('admin/tasks.html', 
                         tasks=tasks_pagination.items,
                         pagination=tasks_pagination,
                         users=all_users,
                         TaskStatus=TaskStatus,
                         TaskPriority=TaskPriority,
                         current_filters={
                             'status': status_filter,
                             'priority': priority_filter,
                             'user_id': int(user_filter) if user_filter else None
                         })

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    try:
        # Tasks will be deleted automatically due to cascade
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{username}" and all their tasks have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user.', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_task(task_id):
    """Delete a task (admin only)"""
    task = Task.query.get_or_404(task_id)
    
    try:
        task_title = task.title
        db.session.delete(task)
        db.session.commit()
        flash(f'Task "{task_title}" has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting task.', 'error')
    
    return redirect(url_for('admin.tasks'))