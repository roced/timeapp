import pytest
from datetime import datetime, UTC
from app.models import User, Event, Memo, EventLike, EventAttendance, EventWishlist

def test_event_relationships(db_session):
    """Test Event model relationships."""
    user = User(
        username='testuser', 
        email='test@example.com',
        role='viewer'
    )
    user.set_password('testpass')
    db_session.add(user)
    db_session.commit()
    
    event = Event(
        title='Test Event',
        description='Test Description',
        start_date=datetime.now(UTC).date(),
        owner_id=user.id,
        is_public=True
    )
    db_session.add(event)
    db_session.commit()
    
    # Test likes
    like = EventLike(user_id=user.id, event_id=event.id)
    db_session.add(like)
    db_session.commit()
    
    # Test attendance
    attendance = EventAttendance(user_id=user.id, event_id=event.id)
    db_session.add(attendance)
    db_session.commit()
    
    # Test wishlist
    wishlist = EventWishlist(user_id=user.id, event_id=event.id)
    db_session.add(wishlist)
    db_session.commit()
    
    db_session.refresh(event)
    db_session.refresh(user)
    
    # Check relationships using query
    assert EventLike.query.filter_by(user_id=user.id, event_id=event.id).first() is not None
    assert EventAttendance.query.filter_by(user_id=user.id, event_id=event.id).first() is not None
    assert EventWishlist.query.filter_by(user_id=user.id, event_id=event.id).first() is not None

def test_user_relationships(db_session):
    """Test User model relationships."""
    user = User(
        username='testuser', 
        email='test@example.com',
        role='viewer'
    )
    user.set_password('testpass')
    db_session.add(user)
    db_session.commit()
    
    event = Event(
        title='Test Event',
        description='Test Description',
        start_date=datetime.now(UTC).date(),
        owner_id=user.id,
        is_public=True
    )
    db_session.add(event)
    
    memo = Memo(
        title='Test Memo',
        content='Test Content',
        user_id=user.id
    )
    db_session.add(memo)
    db_session.commit()
    
    db_session.refresh(user)
    # Check relationships using query
    assert Event.query.filter_by(owner_id=user.id).first() is not None
    assert Memo.query.filter_by(user_id=user.id).first() is not None