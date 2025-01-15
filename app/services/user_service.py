from typing import Optional, List
from ..models import User
from ..extensions import db
from werkzeug.security import generate_password_hash
from flask import current_app
from sqlalchemy import or_

class UserService:
    @staticmethod
    def get_user_count() -> int:
        """Get total number of users."""
        return User.query.count()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username."""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users."""
        return User.query.order_by(User.username).all()

    @staticmethod
    def create_user(data: dict) -> User:
        """Create a new user."""
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'viewer')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user: User, data: dict) -> User:
        """Update user details."""
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        if 'password' in data:
            user.set_password(data['password'])
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user: User) -> None:
        """Delete a user."""
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def verify_password(user: User, password: str) -> bool:
        """Verify user's password."""
        return user.check_password(password)

    @staticmethod
    def create_admin_if_not_exists() -> Optional[User]:
        """Create admin user if it doesn't exist."""
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username=current_app.config['ADMIN_USERNAME'],
                email=current_app.config['ADMIN_EMAIL'],
                role='admin'
            )
            admin.set_password(current_app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            current_app.logger.info('Admin user created')
            return admin
        return None 