import pytest
from app.models import Memo
from app.extensions import db
from datetime import date

def test_create_memo(app, auth_client, test_user, db_session):
    """Test memo creation."""
    with app.app_context():
        response = auth_client.post('/memos/create', data={
            'title': 'Test Memo',
            'content': 'This is a test memo',
            'due_date': '2024-12-31',
            'priority': 'high',
            'status': 'pending'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        memo = db_session.execute(db.select(Memo).filter_by(title='Test Memo')).scalar_one_or_none()
        assert memo is not None
        assert memo.content == 'This is a test memo'
        assert memo.user_id == test_user.id 