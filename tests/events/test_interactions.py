from datetime import date
from app.models import Event, EventLike, EventAttendance, EventWishlist

def test_event_like(app, auth_client, test_user, db_session):
    """Test event liking functionality."""
    with app.app_context():
        event = Event(
            title='Test Event',
            description='Test description',
            start_date=date(2024, 12, 31),
            owner_id=test_user.id,
            is_public=True
        )
        db_session.add(event)
        db_session.commit()

        # Test liking
        response = auth_client.post(f'/events/{event.id}/like')
        assert response.status_code == 200
        
        like = db_session.query(EventLike).filter_by(
            user_id=test_user.id,
            event_id=event.id
        ).first()
        assert like is not None

def test_event_attendance(app, auth_client, test_user, db_session):
    """Test event attendance functionality."""
    with app.app_context():
        event = Event(
            title='Test Event',
            description='Test description',
            start_date=date(2024, 12, 31),
            owner_id=test_user.id,
            is_public=True
        )
        db_session.add(event)
        db_session.commit()

        response = auth_client.post(f'/events/{event.id}/attend')
        assert response.status_code == 200
        
        attendance = db_session.query(EventAttendance).filter_by(
            user_id=test_user.id,
            event_id=event.id
        ).first()
        assert attendance is not None 