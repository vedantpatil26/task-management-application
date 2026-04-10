"""
Database initialization script
Run this once to create all tables and optionally seed sample data
Usage: python init_db.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models.user_model import User
from app.models.task_model import Task, TaskStatus
from datetime import date, timedelta

app = create_app()


def init_db(seed=True):
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        print("✓ Tables created successfully.")

        if seed:
            # Check if already seeded
            if User.query.first():
                print("Database already has data. Skipping seed.")
                return

            print("Seeding sample data...")

            # Create demo users
            admin = User(username='admin', email='admin@taskmaster.com', full_name='Admin User')
            admin.set_password('admin123')

            alice = User(username='alice', email='alice@taskmaster.com', full_name='Alice Johnson')
            alice.set_password('alice123')

            db.session.add_all([admin, alice])
            db.session.flush()  # Get IDs

            # Create sample tasks
            today = date.today()
            tasks = [
                Task(title='Setup project repository',
                     description='Initialize GitHub repo, add README, set up branch strategy.',
                     due_date=today - timedelta(days=5),
                     status=TaskStatus.COMPLETED,
                     remarks='Done. All branches configured.',
                     created_by_id=admin.id, last_updated_by_id=admin.id),
                Task(title='Design database schema',
                     description='Create ER diagram and data dictionary for the task management app.',
                     due_date=today + timedelta(days=3),
                     status=TaskStatus.IN_PROGRESS,
                     remarks='ER diagram complete, data dictionary WIP.',
                     created_by_id=admin.id, last_updated_by_id=alice.id),
                Task(title='Build REST API endpoints',
                     description='Implement CRUD API for tasks using Flask blueprints.',
                     due_date=today + timedelta(days=7),
                     status=TaskStatus.PENDING,
                     created_by_id=alice.id, last_updated_by_id=alice.id),
                Task(title='Implement authentication',
                     description='Add login, logout, and registration with Flask-Login.',
                     due_date=today + timedelta(days=5),
                     status=TaskStatus.COMPLETED,
                     remarks='Fully working with session management.',
                     created_by_id=alice.id, last_updated_by_id=alice.id),
                Task(title='Write unit tests',
                     description='Cover all controller methods with pytest.',
                     due_date=today + timedelta(days=14),
                     status=TaskStatus.PENDING,
                     created_by_id=admin.id, last_updated_by_id=admin.id),
                Task(title='Deploy to staging server',
                     description='Configure Nginx + Gunicorn, set env variables, run migrations.',
                     due_date=today - timedelta(days=1),
                     status=TaskStatus.ON_HOLD,
                     remarks='Blocked — waiting for server credentials.',
                     created_by_id=admin.id, last_updated_by_id=admin.id),
            ]

            db.session.add_all(tasks)
            db.session.commit()
            print("✓ Sample data seeded successfully.")
            print("\nDemo credentials:")
            print("  Username: admin | Password: admin123")
            print("  Username: alice | Password: alice123")


if __name__ == '__main__':
    init_db(seed=True)
