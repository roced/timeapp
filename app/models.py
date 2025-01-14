from datetime import datetime, UTC
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='viewer')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    events = db.relationship('Event', back_populates='owner')
    memos = db.relationship('Memo', backref='user', lazy=True)
    likes = db.relationship('EventLike', backref='user', lazy=True)
    attendances = db.relationship('EventAttendance', backref='user', lazy=True)
    wishlists = db.relationship('EventWishlist', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def has_liked_event(self, event_id):
        return any(like.event_id == event_id for like in self.likes)

    def has_wishlisted_event(self, event_id):
        return any(item.event_id == event_id for item in self.wishlists)

    def is_attending_event(self, event_id):
        return any(attendance.event_id == event_id for attendance in self.attendances)

    def can_edit_event(self, event):
        return self.role == 'admin' or event.owner_id == self.id

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_date = db.Column(db.Date)
    is_multiday = db.Column(db.Boolean, default=False)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(20))
    location = db.Column(db.String(200))
    venue = db.Column(db.String(200))
    is_public = db.Column(db.Boolean, default=False)
    info_link = db.Column(db.String(500))
    tags = db.Column(db.String(500))
    pending_promotion = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', back_populates='events')
    
    likes = db.relationship('EventLike', backref='event', lazy=True)
    attendances = db.relationship('EventAttendance', backref='event', lazy=True)
    wishlists = db.relationship('EventWishlist', backref='event', lazy=True)

    @property
    def like_count(self):
        return len(self.likes)

    @property
    def attendance_count(self):
        return len(self.attendances)

    @property
    def tag_list(self):
        """Returns list of tags, handling both comma and semicolon separators"""
        if not self.tags:
            return []
        # Handle both comma and semicolon separators
        if ';' in self.tags:
            return [tag.strip() for tag in self.tags.split(';') if tag.strip()]
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'venue': self.venue,
            'is_public': self.is_public,
            'tags': self.tag_list,
            'like_count': self.like_count,
            'attendance_count': self.attendance_count,
            'owner': {
                'id': self.owner.id,
                'username': self.owner.username
            }
        }

    @staticmethod
    def get_tag_counts(user_id=None):
        """Get counts of all tags used in events."""
        query = Event.query
        
        if user_id:
            query = query.filter(
                (Event.is_public == True) |  # noqa: E712
                (Event.owner_id == user_id)
            )
        else:
            query = query.filter_by(is_public=True)
        
        # Get all events' tags
        events = query.filter(Event.tags != None).filter(Event.tags != '').all()  # noqa: E711
        
        # Count tags
        tag_counts = {}
        for event in events:
            for tag in event.tag_list:  # Using the updated tag_list property
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
        return dict(sorted(tag_counts.items()))  # Return sorted tags

class EventLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    @staticmethod
    def toggle(user_id, event_id):
        like = EventLike.query.filter_by(user_id=user_id, event_id=event_id).first()
        if like:
            db.session.delete(like)
            action = 'unliked'
        else:
            like = EventLike(user_id=user_id, event_id=event_id)
            db.session.add(like)
            action = 'liked'
        db.session.commit()
        return action

class EventAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    @staticmethod
    def toggle(user_id, event_id):
        attendance = EventAttendance.query.filter_by(user_id=user_id, event_id=event_id).first()
        if attendance:
            db.session.delete(attendance)
            action = 'unattending'
        else:
            attendance = EventAttendance(user_id=user_id, event_id=event_id)
            db.session.add(attendance)
            action = 'attending'
        db.session.commit()
        return action

class EventWishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    @staticmethod
    def toggle(user_id, event_id):
        item = EventWishlist.query.filter_by(user_id=user_id, event_id=event_id).first()
        if item:
            db.session.delete(item)
            action = 'removed'
        else:
            item = EventWishlist(user_id=user_id, event_id=event_id)
            db.session.add(item)
            action = 'added'
        db.session.commit()
        return action

class Memo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    due_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)