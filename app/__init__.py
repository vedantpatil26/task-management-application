"""
TaskMaster Application Factory
Initializes Flask app with all extensions and blueprints
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(base_dir, 'views', 'templates')
    static_folder = os.path.join(base_dir, 'views', 'static')

    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.controllers.task_controller import task_bp
    from app.controllers.main_controller import main_bp

    app.register_blueprint(task_bp, url_prefix='/tasks')
    app.register_blueprint(main_bp)

    return app
