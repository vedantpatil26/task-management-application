"""
Unit Tests for TaskMaster
Run with: pytest tests/
"""

import pytest
from app import create_app, db
from app.models.user_model import User
from app.models.task_model import Task, TaskStatus
from datetime import date, timedelta


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seed_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@test.com', full_name='Test User')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        return user.id


def login(client, username='testuser', password='testpass'):
    return client.post('/auth/login', data={'username': username, 'password': password},
                       follow_redirects=True)


# ── AUTH TESTS ────────────────────────────────

class TestAuth:
    def test_register(self, client, app):
        res = client.post('/auth/register', data={
            'username': 'newuser', 'email': 'new@test.com',
            'full_name': 'New User', 'password': 'pass123', 'confirm_password': 'pass123'
        }, follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            assert User.query.filter_by(username='newuser').first() is not None

    def test_login_valid(self, client, seed_user, app):
        res = login(client)
        assert res.status_code == 200
        assert b'Welcome back' in res.data or b'Dashboard' in res.data

    def test_login_invalid(self, client, seed_user):
        res = client.post('/auth/login', data={'username': 'testuser', 'password': 'wrong'},
                          follow_redirects=True)
        assert b'Invalid' in res.data

    def test_logout(self, client, seed_user):
        login(client)
        res = client.get('/auth/logout', follow_redirects=True)
        assert res.status_code == 200


# ── TASK TESTS ────────────────────────────────

class TestTasks:
    def test_create_task(self, client, seed_user, app):
        login(client)
        res = client.post('/tasks/create', data={
            'title': 'Test Task', 'description': 'A test task',
            'status': 'PENDING', 'due_date': '', 'remarks': ''
        }, follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            task = Task.query.filter_by(title='Test Task').first()
            assert task is not None
            assert task.status == TaskStatus.PENDING

    def test_list_tasks(self, client, seed_user):
        login(client)
        res = client.get('/tasks/')
        assert res.status_code == 200

    def test_task_detail(self, client, seed_user, app):
        login(client)
        client.post('/tasks/create', data={
            'title': 'Detail Task', 'description': 'desc',
            'status': 'PENDING', 'due_date': '', 'remarks': ''
        })
        with app.app_context():
            task = Task.query.filter_by(title='Detail Task').first()
            tid = task.id
        res = client.get(f'/tasks/{tid}')
        assert res.status_code == 200
        assert b'Detail Task' in res.data

    def test_update_task(self, client, seed_user, app):
        login(client)
        client.post('/tasks/create', data={
            'title': 'To Update', 'description': 'old', 'status': 'PENDING',
            'due_date': '', 'remarks': ''
        })
        with app.app_context():
            task = Task.query.filter_by(title='To Update').first()
            tid = task.id
        res = client.post(f'/tasks/{tid}/edit', data={
            'title': 'Updated Title', 'description': 'new desc',
            'status': 'IN_PROGRESS', 'due_date': '', 'remarks': 'updated'
        }, follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            task = Task.query.get(tid)
            assert task.title == 'Updated Title'
            assert task.status == TaskStatus.IN_PROGRESS

    def test_delete_task(self, client, seed_user, app):
        login(client)
        client.post('/tasks/create', data={
            'title': 'To Delete', 'description': '', 'status': 'PENDING',
            'due_date': '', 'remarks': ''
        })
        with app.app_context():
            task = Task.query.filter_by(title='To Delete').first()
            tid = task.id
        res = client.post(f'/tasks/{tid}/delete', follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            assert Task.query.get(tid) is None

    def test_search_tasks(self, client, seed_user):
        login(client)
        client.post('/tasks/create', data={
            'title': 'Searchable Task', 'description': 'find me',
            'status': 'PENDING', 'due_date': '', 'remarks': ''
        })
        res = client.get('/tasks/search?q=Searchable')
        assert res.status_code == 200
        assert b'Searchable Task' in res.data

    def test_task_model_is_overdue(self, app, seed_user):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            task = Task(
                title='Overdue Task',
                due_date=date.today() - timedelta(days=2),
                status=TaskStatus.PENDING,
                created_by_id=user.id,
                last_updated_by_id=user.id
            )
            db.session.add(task)
            db.session.commit()
            assert task.is_overdue is True
