from typing import List, Optional
from datetime import date, datetime
from ..models import Event, EventLike, EventAttendance, WishlistItem
from ..extensions import db
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class EventService:
    @staticmethod
    def get_user_events(user_id: int, page: int = 1, per_page: int = 20) -> List[Event]:
        """Get paginated list of events for a user."""
        try:
            return Event.query.filter_by(owner_id=user_id)\
                            .order_by(Event.start_date.desc())\
                            .paginate(page=page, per_page=per_page)
        except Exception as e:
            logger.error(f"Error fetching events for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_public_events(page: int = 1, per_page: int = 20) -> List[Event]:
        """Get paginated list of public events."""
        try:
            return Event.query.filter_by(is_public=True)\
                            .order_by(Event.start_date.desc())\
                            .paginate(page=page, per_page=per_page)
        except Exception as e:
            logger.error(f"Error fetching public events: {str(e)}")
            raise

    @staticmethod
    def create_event(owner_id: int, **event_data) -> Event:
        """Create a new event."""
        try:
            event = Event(owner_id=owner_id, **event_data)
            db.session.add(event)
            db.session.commit()
            logger.info(f"Created event {event.id} by user {owner_id}")
            return event
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating event for user {owner_id}: {str(e)}")
            raise

    @staticmethod
    def update_event(event_id: int, **event_data) -> Event:
        """Update an existing event."""
        try:
            event = Event.query.get_or_404(event_id)
            for key, value in event_data.items():
                setattr(event, key, value)
            db.session.commit()
            logger.info(f"Updated event {event_id}")
            return event
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating event {event_id}: {str(e)}")
            raise

    @staticmethod
    def delete_event(event_id: int) -> None:
        """Delete an event."""
        try:
            event = Event.query.get_or_404(event_id)
            db.session.delete(event)
            db.session.commit()
            logger.info(f"Deleted event {event_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting event {event_id}: {str(e)}")
            raise

    @staticmethod
    def toggle_wishlist(event_id: int, user_id: int) -> bool:
        """Toggle event wishlist status for a user."""
        try:
            wishlist_item = WishlistItem.query.filter_by(
                event_id=event_id,
                user_id=user_id
            ).first()

            if wishlist_item:
                db.session.delete(wishlist_item)
                db.session.commit()
                logger.info(f"Removed event {event_id} from wishlist for user {user_id}")
                return False
            else:
                wishlist_item = WishlistItem(event_id=event_id, user_id=user_id)
                db.session.add(wishlist_item)
                db.session.commit()
                logger.info(f"Added event {event_id} to wishlist for user {user_id}")
                return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error toggling wishlist for event {event_id}, user {user_id}: {str(e)}")
            raise