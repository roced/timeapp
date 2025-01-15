from typing import List, Optional, Dict
from datetime import datetime
from ..models import Event, EventLike, EventAttendance, EventWishlist
from ..extensions import db
from sqlalchemy import or_
from flask import current_app

class EventService:
    @staticmethod
    def get_events(user_id: Optional[int] = None) -> List[Event]:
        """Get all public events and user's private events."""
        if user_id:
            return Event.query.filter(
                or_(
                    Event.is_public == True,  # noqa: E712
                    Event.owner_id == user_id
                )
            ).order_by(Event.start_date.desc()).all()
        return Event.query.filter_by(is_public=True).order_by(Event.start_date.desc()).all()

    @staticmethod
    def get_event_by_id(event_id: int, user_id: Optional[int] = None) -> Optional[Event]:
        """Get event by ID, considering visibility permissions."""
        event = Event.query.get_or_404(event_id)
        if event.is_public or (user_id and event.owner_id == user_id):
            return event
        return None

    @staticmethod
    def create_event(data: dict, owner_id: int) -> Event:
        """Create a new event."""
        event = Event(
            title=data['title'],
            description=data['description'],
            start_date=data['start_date'],
            start_time=data['start_time'],
            is_multiday=data['is_multiday'],
            end_date=data['end_date'] if data['is_multiday'] else None,
            is_recurring=data['is_recurring'],
            recurrence_pattern=data['recurrence_pattern'] if data['is_recurring'] else None,
            location=data['location'],
            venue=data['venue'],
            is_public=data['is_public'],
            info_link=data['info_link'],
            tags=data['tags'],
            owner_id=owner_id
        )
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def update_event(event: Event, data: dict) -> Event:
        """Update an existing event."""
        event.title = data['title']
        event.description = data['description']
        event.start_date = data['start_date']
        event.start_time = data['start_time']
        event.is_multiday = data['is_multiday']
        event.end_date = data['end_date'] if data['is_multiday'] else None
        event.is_recurring = data['is_recurring']
        event.recurrence_pattern = data['recurrence_pattern'] if data['is_recurring'] else None
        event.location = data['location']
        event.venue = data['venue']
        event.is_public = data['is_public']
        event.info_link = data['info_link']
        event.tags = data['tags']
        
        db.session.commit()
        return event

    @staticmethod
    def delete_event(event: Event) -> None:
        """Delete an event."""
        db.session.delete(event)
        db.session.commit()

    @staticmethod
    def toggle_like(event_id: int, user_id: int) -> bool:
        """Toggle like status for an event."""
        like = EventLike.query.filter_by(
            event_id=event_id, 
            user_id=user_id
        ).first()
        
        if like:
            db.session.delete(like)
            db.session.commit()
            return False
        
        like = EventLike(event_id=event_id, user_id=user_id)
        db.session.add(like)
        db.session.commit()
        return True

    @staticmethod
    def toggle_attendance(event_id: int, user_id: int) -> bool:
        """Toggle attendance status for an event."""
        attendance = EventAttendance.query.filter_by(
            event_id=event_id,
            user_id=user_id
        ).first()

        if attendance:
            db.session.delete(attendance)
            db.session.commit()
            return False

        attendance = EventAttendance(event_id=event_id, user_id=user_id)
        db.session.add(attendance)
        db.session.commit()
        return True

    @staticmethod
    def toggle_wishlist(event_id: int, user_id: int) -> bool:
        """Toggle wishlist status for an event."""
        wishlist = EventWishlist.query.filter_by(
            event_id=event_id,
            user_id=user_id
        ).first()

        if wishlist:
            db.session.delete(wishlist)
            db.session.commit()
            return False

        wishlist = EventWishlist(event_id=event_id, user_id=user_id)
        db.session.add(wishlist)
        db.session.commit()
        return True

    @staticmethod
    def request_promotion(event_id: int, user_id: int) -> bool:
        """Request promotion for an event."""
        event = Event.query.get_or_404(event_id)
        if event.owner_id != user_id:
            return False
        
        event.pending_promotion = True
        db.session.commit()
        return True

    @staticmethod
    def approve_promotion(event_id: int) -> bool:
        """Approve promotion request for an event."""
        event = Event.query.get_or_404(event_id)
        event.pending_promotion = False
        event.is_public = True
        db.session.commit()
        return True

    @staticmethod
    def reject_promotion(event_id: int) -> bool:
        """Reject promotion request for an event."""
        event = Event.query.get_or_404(event_id)
        event.pending_promotion = False
        db.session.commit()
        return True

    @staticmethod
    def get_calendar_events(user_id: Optional[int] = None) -> List[Event]:
        """Get events for calendar view."""
        if user_id:
            return Event.query.filter(
                or_(
                    Event.is_public == True,  # noqa: E712
                    Event.owner_id == user_id
                )
            ).order_by(Event.start_date.desc()).all()
        return Event.query.filter_by(is_public=True).order_by(Event.start_date.desc()).all()

    @staticmethod
    def get_event_count() -> int:
        """Get total number of events."""
        return Event.query.count()

    @staticmethod
    def get_pending_promotions_count() -> int:
        """Get count of events pending promotion."""
        return Event.query.filter_by(pending_promotion=True).count()

    @staticmethod
    def get_recent_events(limit: int = 5) -> List[Event]:
        """Get most recent events."""
        return Event.query.order_by(Event.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_all_events() -> List[Event]:
        """Get all events for admin view."""
        return Event.query.order_by(Event.created_at.desc()).all()

    @staticmethod
    def get_pending_promotions() -> List[Event]:
        """Get all events pending promotion."""
        return Event.query.filter_by(pending_promotion=True).order_by(Event.created_at.desc()).all()

    @staticmethod
    def bulk_create_events(csv_data: List[dict], owner_id: int) -> int:
        """Create multiple events from CSV data."""
        success_count = 0
        for row in csv_data:
            try:
                event = Event(
                    title=row.get('title'),
                    description=row.get('description', ''),
                    start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                    start_time=datetime.strptime(row['start_time'], '%H:%M').time() if row.get('start_time') else None,
                    is_multiday=bool(row.get('is_multiday')),
                    end_date=datetime.strptime(row['end_date'], '%Y-%m-%d').date() if row.get('end_date') else None,
                    location=row.get('location'),
                    venue=row.get('venue'),
                    is_public=bool(row.get('is_public')),
                    owner_id=owner_id,
                    tags=row.get('tags', '')
                )
                db.session.add(event)
                success_count += 1
            except Exception as e:
                current_app.logger.error(f"Error creating event from CSV: {str(e)}")
                continue
        
        db.session.commit()
        return success_count