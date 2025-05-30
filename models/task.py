from datetime import datetime, timezone
from enum import Enum
from models import db
import pytz

# South African timezone
SAST = pytz.timezone('Africa/Johannesburg')

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    
class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
class Task(db.Model):
    __tablename__ = "tasks"
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Task details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Status and priority
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    # Dates
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(SAST), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(SAST), onupdate=datetime.now(SAST))
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'

    def to_dict(self):
        return{
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    @property
    def is_completed(self):
        """Check if task is completed"""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.due_date:
            return False
        return datetime.now(SAST) > self.due_date and self.is_completed

    def mark_completed(self):
        """Mark as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now(SAST)
        self.updated_at = datetime.now(SAST)
        
    def mark_pending(self):
        """Mark task as pending (reopen)"""
        self.status = TaskStatus.PENDING
        self.completed_at = None
        self.updated_at = datetime.now(SAST)
        
    def mark_in_progress(self):
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now(SAST)
        
    def toggle_completion(self):
        """Toggle task completion status"""
        if self.is_completed:
            self.mark_pending()
        else:
            self.mark_completed()
        
    @classmethod
    def get_by_status(cls, status):
        return cls.query.filter_by(status=status).all()
    
    @classmethod
    def get_by_priority(cls, priority):
        return cls.query.filter_by(priority=priority).all()
    