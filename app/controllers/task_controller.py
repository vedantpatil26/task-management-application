"""
Task Controller (MVC - Controller Layer)
Handles all CRUD operations and search for Tasks
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy import or_
from app import db
from app.models.task_model import Task, TaskStatus

task_bp = Blueprint('tasks', __name__)


def _parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


# ─── CREATE ───────────────────────────────────────────────────────────────────

@task_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date_str = request.form.get('due_date', '')
        status_str = request.form.get('status', 'PENDING')
        remarks = request.form.get('remarks', '').strip()

        if not title:
            flash('Task title is required.', 'danger')
            return render_template('tasks/create.html',
                                   statuses=TaskStatus, form_data=request.form)

        try:
            status = TaskStatus[status_str]
        except KeyError:
            status = TaskStatus.PENDING

        task = Task(
            title=title,
            description=description or None,
            due_date=_parse_date(due_date_str),
            status=status,
            remarks=remarks or None,
            created_by_id=1,
            last_updated_by_id=1,
        )
        db.session.add(task)
        db.session.commit()

        flash(f'Task "{task.title}" created successfully!', 'success')
        return redirect(url_for('tasks.detail', task_id=task.id))

    return render_template('tasks/create.html', statuses=TaskStatus)


# ─── READ / LIST ──────────────────────────────────────────────────────────────

@task_bp.route('/')
def list_tasks():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'created_on')
    order = request.args.get('order', 'desc')

    query = Task.query

    if status_filter:
        try:
            query = query.filter(Task.status == TaskStatus[status_filter])
        except KeyError:
            pass

    sort_column = getattr(Task, sort_by, Task.created_on)
    if order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('tasks/list.html',
                           tasks=pagination.items,
                           pagination=pagination,
                           statuses=TaskStatus,
                           current_status=status_filter,
                           sort_by=sort_by,
                           order=order)


# ─── DETAIL ───────────────────────────────────────────────────────────────────

@task_bp.route('/<int:task_id>')
def detail(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('tasks/detail.html', task=task)


# ─── UPDATE ───────────────────────────────────────────────────────────────────

@task_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date_str = request.form.get('due_date', '')
        status_str = request.form.get('status', 'PENDING')
        remarks = request.form.get('remarks', '').strip()

        if not title:
            flash('Task title is required.', 'danger')
            return render_template('tasks/edit.html', task=task, statuses=TaskStatus)

        try:
            status = TaskStatus[status_str]
        except KeyError:
            status = task.status

        task.title = title
        task.description = description or None
        task.due_date = _parse_date(due_date_str)
        task.status = status
        task.remarks = remarks or None
        task.last_updated_on = datetime.utcnow()
        task.last_updated_by_id = 1

        db.session.commit()
        flash(f'Task "{task.title}" updated successfully!', 'success')
        return redirect(url_for('tasks.detail', task_id=task.id))

    return render_template('tasks/edit.html', task=task, statuses=TaskStatus)


# ─── DELETE ───────────────────────────────────────────────────────────────────

@task_bp.route('/<int:task_id>/delete', methods=['POST'])
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    title = task.title
    db.session.delete(task)
    db.session.commit()
    flash(f'Task "{title}" deleted successfully.', 'success')
    return redirect(url_for('tasks.list_tasks'))


# ─── SEARCH ───────────────────────────────────────────────────────────────────

@task_bp.route('/search')
def search():
    query_str = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')
    due_before = request.args.get('due_before', '')
    due_after = request.args.get('due_after', '')
    page = request.args.get('page', 1, type=int)

    query = Task.query

    if query_str:
        search_term = f'%{query_str}%'
        query = query.filter(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
                Task.remarks.ilike(search_term),
            )
        )

    if status_filter:
        try:
            query = query.filter(Task.status == TaskStatus[status_filter])
        except KeyError:
            pass

    if due_before:
        parsed = _parse_date(due_before)
        if parsed:
            query = query.filter(Task.due_date <= parsed)

    if due_after:
        parsed = _parse_date(due_after)
        if parsed:
            query = query.filter(Task.due_date >= parsed)

    query = query.order_by(Task.created_on.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('tasks/search.html',
                           tasks=pagination.items,
                           pagination=pagination,
                           statuses=TaskStatus,
                           query_str=query_str,
                           status_filter=status_filter,
                           due_before=due_before,
                           due_after=due_after)


# ─── API ENDPOINT (JSON) ──────────────────────────────────────────────────────

@task_bp.route('/api/tasks')
def api_tasks():
    """REST API endpoint for tasks - returns JSON"""
    tasks = Task.query.order_by(Task.created_on.desc()).all()
    return jsonify([t.to_dict() for t in tasks])
