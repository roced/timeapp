import pytest
from app.models import Event, EventLike, EventAttendance, EventWishlist
from app.extensions import db
from datetime import date

def test_create_event(app, auth_client, test_user, db_session):
    """Test event creation."""
    with app.app_context():
        response = auth_client.post('/events/create', data={
            'title': 'Test Event',
            'description': 'This is a test event',
            'start_date': '2024-12-31',
            'start_time': '14:00',
            'end_date': '2024-12-31',
            'location': 'Test Location',
            'venue': 'Test Venue',
            'is_public': True,
            'is_recurring': False,
            'info_link': 'https://example.com',
            'tags': 'test;event;demo'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        stmt = db.select(Event).filter_by(title='Test Event')
        event = db_session.execute(stmt).scalar_one_or_none()
        assert event is not None
        assert event.description == 'This is a test event'
        assert event.owner_id == test_user.id 