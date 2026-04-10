"""
Main Controller (MVC - Controller Layer)
Handles dashboard and home page
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.task_model import Task, TaskStatus
from sqlalchemy import func
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return redirect(url_for('tasks.list_tasks'))


@main_bp.route('/dashboard')
def dashboard():
    # Stats for dashboard
    total = Task.query.count()
    pending = Task.query.filter_by(status=TaskStatus.PENDING).count()
    in_progress = Task.query.filter_by(status=TaskStatus.IN_PROGRESS).count()
    completed = Task.query.filter_by(status=TaskStatus.COMPLETED).count()
    on_hold = Task.query.filter_by(status=TaskStatus.ON_HOLD).count()
    cancelled = Task.query.filter_by(status=TaskStatus.CANCELLED).count()

    today = datetime.utcnow().date()
    overdue = Task.query.filter(
        Task.due_date < today,
        Task.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED])
    ).count()

    recent_tasks = Task.query.order_by(Task.created_on.desc()).limit(5).all()

    stats = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'on_hold': on_hold,
        'cancelled': cancelled,
        'overdue': overdue,
    }

    return render_template('main/dashboard.html', stats=stats, recent_tasks=recent_tasks)
