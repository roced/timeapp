from typing import List, Dict, Any
from sqlalchemy import or_
from ..models import Event, Memo
from datetime import datetime

class SearchService:
    @staticmethod
    def search_events(query: str, user_id: int = None) -> List[Event]:
        """Search events by title, description, location, or tags."""
        search = f"%{query}%"
        events = Event.query.filter(
            or_(
                Event.title.ilike(search),
                Event.description.ilike(search),
                Event.location.ilike(search),
                Event.tags.ilike(search)  # Works with semicolon-separated tags
            )
        )
        
        if user_id:
            events = events.filter(
                or_(
                    Event.owner_id == user_id,
                    Event.is_public == True  # noqa: E712
                )
            )
        else:
            events = events.filter(Event.is_public == True)  # noqa: E712
            
        return events.order_by(Event.start_date.desc()).all()

    @staticmethod
    def search_memos(query: str, user_id: int) -> List[Memo]:
        """Search user's memos by title or content."""
        search = f"%{query}%"
        return Memo.query.filter(
            Memo.user_id == user_id,
            or_(
                Memo.title.ilike(search),
                Memo.content.ilike(search)
            )
        ).order_by(Memo.created_at.desc()).all() 