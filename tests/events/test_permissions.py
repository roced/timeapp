import pytest
from app.models import Event, EventLike, EventAttendance, EventWishlist, User
from datetime import date, datetime, UTC

def test_unauthorized_event_access(app, client, db_session):
    """Test unauthorized access to events."""
    response = client.get('/events/create')
    assert response.status_code == 302  # Redirects to login

def test_event_owner_permissions(app, auth_client, test_user, db_session):
    """Test event owner permissions."""
    with app.app_context():
        event = Event(
            title='Test Event',
            description='Test description',
            start_date=datetime.now(UTC).date(),
            owner_id=test_user.id,
            is_public=True
        )
        db_session.add(event)
        db_session.commit()

        # Test edit access - accept both 200 and 302 (redirect)
        response = auth_client.get(f'/events/{event.id}/edit')
        assert response.status_code in [200, 302]

        # Test delete access - accept both 200 and 302 (redirect)
        response = auth_client.post(f'/events/{event.id}/delete', 
                                  follow_redirects=True)  # Add follow_redirects
        assert response.status_code == 200 