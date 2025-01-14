import pytest
from app.models import Memo, User
from datetime import date

def test_unauthorized_memo_access(app, client, test_user, db_session):
    """Test unauthorized memo access."""
    with app.app_context():
        memo = Memo(
            title='Test Memo',
            content='Test content',
            user_id=test_user.id
        )
        db_session.add(memo)
        db_session.commit()

        # Should get 404 for unauthorized access
        response = client.get(f'/memos/{memo.id}/view')
        assert response.status_code == 404  # Expect 404 instead of redirect

def test_memo_owner_permissions(app, auth_client, test_user, db_session):
    """Test memo owner permissions."""
    with app.app_context():
        memo = Memo(
            title='Test Memo',
            content='Test content',
            user_id=test_user.id
        )
        db_session.add(memo)
        db_session.commit()

        # Test edit access
        response = auth_client.get(f'/memos/{memo.id}/edit')
        assert response.status_code in [200, 302]

        # Test delete access
        response = auth_client.post(f'/memos/{memo.id}/delete',
                                  follow_redirects=True)
        assert response.status_code == 200
        
        # Use db.session.get instead of Query.get
        deleted_memo = db_session.get(Memo, memo.id)
        assert deleted_memo is None 