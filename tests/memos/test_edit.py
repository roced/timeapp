import pytest
from app.models import Memo
from datetime import date

def test_edit_memo(app, auth_client, test_user, db_session):
    """Test memo editing."""
    with app.app_context():
        memo = Memo(
            title='Original Memo',
            content='Original content',
            user_id=test_user.id
        )
        db_session.add(memo)
        db_session.commit()

        response = auth_client.post(f'/memos/{memo.id}/edit', data={
            'title': 'Updated Memo',
            'content': 'Updated content',
            'due_date': '2024-12-31',
            'priority': 'medium',
            'status': 'pending'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        updated_memo = db_session.get(Memo, memo.id)
        assert updated_memo.title == 'Updated Memo'
        assert updated_memo.content == 'Updated content' 