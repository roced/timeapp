import pytest
from app.models import Event, EventLike, EventAttendance, EventWishlist
from datetime import date

def test_delete_event(app, auth_client, test_user, db_session):
    """Test event deletion."""
    with app.app_context():
        event = Event(
            title='Test Event',
            description='This will be deleted',
            start_date=date(2024, 12, 31),
            owner_id=test_user.id,
            is_public=True
        )
        db_session.add(event)
        db_session.commit()
        event_id = event.id

        response = auth_client.post(f'/events/{event_id}/delete', 
                                  follow_redirects=True)
        
        assert response.status_code == 200
        event = db_session.get(Event, event_id)
        assert event is None 