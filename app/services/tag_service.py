from typing import Set, Dict, List
from sqlalchemy import or_
from ..models import Event
from datetime import datetime

class TagService:
    @staticmethod
    def get_available_tags(user_id: int = None) -> Set[str]:
        """Get all available tags from public events (and user's private events if user_id provided)."""
        query = Event.query.filter(
            Event.tags != None,  # noqa: E711
            Event.tags != ''
        )

        if user_id:
            query = query.filter(
                or_(
                    Event.is_public == True,  # noqa: E712
                    Event.owner_id == user_id
                )
            )
        else:
            query = query.filter(Event.is_public == True)  # noqa: E712

        events = query.all()
        tags = set()
        for event in events:
            tags.update(event.tag_list)
        return tags

    @staticmethod
    def filter_events_by_tags(included_tags: Set[str], excluded_tags: Set[str], user_id: int = None) -> List[Event]:
        """Filter events based on included and excluded tags."""
        query = Event.query

        if user_id:
            query = query.filter(
                or_(
                    Event.is_public == True,  # noqa: E712
                    Event.owner_id == user_id
                )
            )
        else:
            query = query.filter(Event.is_public == True)  # noqa: E712

        # Include tags
        for tag in included_tags:
            query = query.filter(Event.tags.contains(tag))

        # Exclude tags
        for tag in excluded_tags:
            query = query.filter(~Event.tags.contains(tag))

        return query.order_by(Event.start_date.desc()).all()

    @staticmethod
    def get_tag_counts(user_id: int = None) -> Dict[str, int]:
        """Get counts of all tags used in events."""
        query = Event.query

        if user_id:
            query = query.filter(
                or_(
                    Event.is_public == True,  # noqa: E712
                    Event.owner_id == user_id
                )
            )
        else:
            query = query.filter(Event.is_public == True)  # noqa: E712

        events = query.filter(Event.tags != None).filter(Event.tags != '').all()  # noqa: E711
        
        tag_counts = {}
        for event in events:
            for tag in event.tag_list:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
        return dict(sorted(tag_counts.items())) 