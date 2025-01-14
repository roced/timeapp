from flask import Flask

from .extensions import db, migrate, login_manager
import os
from .utils import nl2br
from .config import config

def create_app(config_name='default'):
    app = Flask(__name__)

    
    # Get the config class from the dictionary
    config_class = config['development']
    app.config.from_object(config_class)
    config_class.init_app(app)  # Initialize logging
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from .auth import auth
    app.register_blueprint(auth)

    from .main import main
    app.register_blueprint(main)

    from .events import events
    app.register_blueprint(events)

    from .memos import memos
    app.register_blueprint(memos)

    from .api import api
    app.register_blueprint(api, url_prefix='/api')

    from .admin import admin
    app.register_blueprint(admin)

    from .errors import errors
    app.register_blueprint(errors)

    @login_manager.user_loader
    def load_user(id):
        from .models import User
        return db.session.get(User, int(id))

    # Only initialize admin in production/development AND after migrations
    if not app.config.get('TESTING'):
        with app.app_context():
            try:
                # Check if tables exist before initializing admin
                from .models import User
                User.query.first()
                from .db_init import init_admin
                init_admin(app)
            except Exception as e:
                # Tables don't exist yet, skip admin creation
                pass

    # Register Jinja filters
    app.jinja_env.filters['nl2br'] = nl2br

    return app 