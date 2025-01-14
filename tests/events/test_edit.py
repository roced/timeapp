import pytest
from app.models import Event, EventLike, EventAttendance, EventWishlist
from datetime import date, datetime, UTC

def test_edit_event(app, auth_client, test_user, db_session):
    """Test event editing."""
    with app.app_context():
        event = Event(
            title='Original Event',
            description='Original description',
            start_date=datetime.now(UTC).date(),
            owner_id=test_user.id,
            is_public=True
        )
        db_session.add(event)
        db_session.commit()

        response = auth_client.post(f'/events/{event.id}/edit', data={
            'title': 'Updated Event',
            'description': 'Updated description',
            'start_date': '2024-12-31',
            'start_time': '14:00',
            'end_date': '2024-12-31',
            'location': 'Updated Location',
            'venue': 'Updated Venue',
            'is_public': True,
            'is_recurring': True,
            'info_link': 'https://updated.com',
            'tags': 'updated;test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        updated_event = db_session.get(Event, event.id)
        assert updated_event is not None
        assert updated_event.title == 'Updated Event'
        assert updated_event.description == 'Updated description'