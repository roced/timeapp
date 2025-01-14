from flask import current_app
import logging
from .models import User, db
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

def init_admin(app):
    """Initialize admin user if it doesn't exist."""
    try:
        # Check if the admin user exists
        admin = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
        if admin:
            logger.info("Admin user already exists.")
            return

        # Create admin user if not exists
        admin = User(
            username=app.config['ADMIN_USERNAME'],
            email=app.config['ADMIN_EMAIL'],
            role='admin'
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created successfully.")
        
    except OperationalError as e:
        # This will happen when tables don't exist yet - that's okay
        logger.info("Database tables not ready yet - skipping admin creation")
        return
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return 