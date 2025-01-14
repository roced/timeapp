from typing import List, Optional
from datetime import date
from ..models import Memo
from ..extensions import db
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class MemoService:
    @staticmethod
    def get_user_memos(user_id: int, page: int = 1, per_page: int = 20) -> List[Memo]:
        """Get paginated list of memos for a user.

        Args:
            user_id: The ID of the user
            page: Page number (default: 1)
            per_page: Items per page (default: 20)

        Returns:
            List of Memo objects
        """
        try:
            return Memo.query.filter_by(user_id=user_id)\
                           .order_by(Memo.created_at.desc())\
                           .paginate(page=page, per_page=per_page)
        except Exception as e:
            logger.error(f"Error fetching memos for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def create_memo(user_id: int, title: str, content: str, 
                   due_date: Optional[date] = None) -> Memo:
        """Create a new memo.

        Args:
            user_id: The ID of the user creating the memo
            title: Memo title
            content: Memo content
            due_date: Optional due date

        Returns:
            Created Memo object
        """
        try:
            memo = Memo(
                user_id=user_id,
                title=title,
                content=content,
                due_date=due_date
            )
            db.session.add(memo)
            db.session.commit()
            logger.info(f"Created memo {memo.id} for user {user_id}")
            return memo
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating memo for user {user_id}: {str(e)}")
            raise 