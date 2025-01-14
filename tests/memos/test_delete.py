import pytest
from app.models import Memo
from datetime import date
from app.extensions import db

def test_delete_memo(app, auth_client, test_user, db_session):
    """Test memo deletion."""
    with app.app_context():
        memo = Memo(
            title='Test Memo',
            content='This will be deleted',
            user_id=test_user.id
        )
        db_session.add(memo)
        db_session.commit()
        memo_id = memo.id

        response = auth_client.post(f'/memos/{memo_id}/delete', 
                                  follow_redirects=True)
        
        assert response.status_code in [200, 302]
        memo = db_session.get(Memo, memo_id)
        assert memo is None 