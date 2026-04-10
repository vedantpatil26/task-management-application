"""
Task Model
Core data structure for the Task Management application
Includes all required fields as per assignment specification
"""

from datetime import datetime
import enum
from app import db


class TaskStatus(enum.Enum):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    ON_HOLD = 'On Hold'
    CANCELLED = 'Cancelled'


class Task(db.Model):
    __tablename__ = 'tasks'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core task fields (as per assignment data structure)
    title = db.Column(db.String(200), nullable=False)                         # Task Title
    description = db.Column(db.Text, nullable=True)                           # Task Description
    due_date = db.Column(db.Date, nullable=True)                              # Task Due Date
    status = db.Column(
        db.Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING
    )                                                                          # Task Status
    remarks = db.Column(db.Text, nullable=True)                               # Task Remarks

    # Audit timestamps
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)       # Created On (Time Stamp)
    last_updated_on = db.Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow, onupdate=datetime.utcnow
    )                                                                                   # Last Updated on (Time Stamp)

    # User tracking (FK references)
    created_by_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )                                                                          # Created By ID
    last_updated_by_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )                                                                          # Last Updated By ID

    # Indexes for performance
    __table_args__ = (
        db.Index('idx_tasks_status', 'status'),
        db.Index('idx_tasks_due_date', 'due_date'),
        db.Index('idx_tasks_created_by', 'created_by_id'),
        db.Index('idx_tasks_created_on', 'created_on'),
        db.Index('idx_tasks_title', 'title'),
    )

    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status.value,
            'remarks': self.remarks,
            'created_on': self.created_on.isoformat(),
            'last_updated_on': self.last_updated_on.isoformat(),
            'created_by_id': self.created_by_id,
            'created_by_name': self.creator.full_name if self.creator else None,
            'last_updated_by_id': self.last_updated_by_id,
            'last_updated_by_name': self.updater.full_name if self.updater else None,
        }

    @property
    def is_overdue(self):
        if self.due_date and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return self.due_date < datetime.utcnow().date()
        return False
