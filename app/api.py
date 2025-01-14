from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from .models import Event, EventLike, EventAttendance, EventWishlist
from .extensions import db
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/events')
def get_events():
    """
    Get filtered events
    Query params: tag, search, filter_by
    """
    try:
        tag = request.args.get('tag')
        search = request.args.get('search')
        filter_by = request.args.get('filter_by')
        
        query = Event.query.filter_by(is_public=True)
        
        if tag:
            query = query.filter(Event.tags.contains(tag))
        if search:
            query = query.filter(
                (Event.title.ilike(f'%{search}%')) |
                (Event.description.ilike(f'%{search}%')) |
                (Event.location.ilike(f'%{search}%'))
            )
        if filter_by == 'upcoming':
            query = query.filter(Event.start_date >= datetime.now().date())
        current_app.logger.info('Fetching events')
        events = query.order_by(Event.start_date).all()
        current_app.logger.info(f'Found {len(events)} events')
        return jsonify({
            'events': [{
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start_date': event.start_date.strftime('%Y-%m-%d'),
                'end_date': event.end_date.strftime('%Y-%m-%d') if event.end_date else None,
                'location': event.location,
                'venue': event.venue,
                'tags': event.tags.split(',') if event.tags else [],
                'like_count': event.like_count,
                'attendance_count': event.attendance_count,
                'is_liked': bool(current_user.is_authenticated and 
                               event.likes.filter_by(user_id=current_user.id).first()),
                'is_attending': bool(current_user.is_authenticated and 
                                   event.attendances.filter_by(user_id=current_user.id).first())
            } for event in events]
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_events: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/events/<int:event_id>/like', methods=['POST'])
@login_required
def toggle_like(event_id):
    event = Event.query.get_or_404(event_id)
    like = EventLike.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if like:
        db.session.delete(like)
    else:
        like = EventLike(user_id=current_user.id, event_id=event_id)
        db.session.add(like)
    
    db.session.commit()
    return jsonify({
        'success': True,
        'liked': like is not None,
        'count': event.like_count
    })

@api.route('/events/<int:event_id>/attend', methods=['POST'])
@login_required
def toggle_attend(event_id):
    event = Event.query.get_or_404(event_id)
    attendance = EventAttendance.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id
    ).first()
    
    if attendance:
        db.session.delete(attendance)
    else:
        attendance = EventAttendance(user_id=current_user.id, event_id=event_id)
        db.session.add(attendance)
    
    db.session.commit()
    return jsonify({
        'success': True,
        'attending': attendance is not None,
        'count': event.attendance_count
    })

@api.route('/events/<int:event_id>/wishlist', methods=['POST'])
@login_required
def toggle_wishlist(event_id):
    event = Event.query.get_or_404(event_id)
    wishlist_item = EventWishlist.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id
    ).first()
    
    if wishlist_item:
        db.session.delete(wishlist_item)
    else:
        wishlist_item = EventWishlist(user_id=current_user.id, event_id=event_id)
        db.session.add(wishlist_item)
    
    db.session.commit()
    return jsonify({
        'success': True,
        'in_wishlist': wishlist_item is not None
    }) 