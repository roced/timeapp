from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import config
from .extensions import db, login_manager
from .services.user_service import UserService
import logging

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info('TimeApp startup')
    
    # Import models to ensure they're registered
    from . import models  # This is important!
    
    # Create admin user during app context
    with app.app_context():
        UserService.create_admin_if_not_exists()
    
    # Register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .events import events as events_blueprint
    app.register_blueprint(events_blueprint)
    
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    
    return app 