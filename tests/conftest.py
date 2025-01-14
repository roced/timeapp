import os
import tempfile
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Event, Memo
import uuid
from flask_login import login_user
from flask import session
from sqlalchemy.orm import Session, scoped_session, sessionmaker

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for the entire test session."""
    db_fd, db_path = tempfile.mkstemp()
    
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key',
        'LOGIN_DISABLED': False
    }
    
    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def db_session(app):
    """Create a new database session for each test."""
    with app.app_context():
        # Create a new connection
        connection = db.engine.connect()
        
        # Begin a non-ORM transaction
        transaction = connection.begin()
        
        # Create session factory
        factory = sessionmaker(bind=connection)
        
        # Create scoped session
        session = scoped_session(factory)
        
        # Override the default session
        old_session = db.session
        db.session = session
        
        yield session
        
        # Cleanup after each test
        session.remove()
        transaction.rollback()  # Roll back all changes
        connection.close()
        db.session = old_session

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def test_user(app, db_session):
    """Create and return a test user."""
    user = User(
        username='testuser',
        email='test@example.com',
        role='viewer'
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope='function')
def auth_client(app, client, test_user):
    """A test client with an authenticated user."""
    with app.test_request_context():
        login_user(test_user)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
            sess['_fresh'] = True
    return client 