from flask import Blueprint, render_template, request
from flask_login import current_user
from .models import Event, EventAttendance, EventWishlist
from .extensions import db
from datetime import datetime, UTC
from sqlalchemy import or_, and_

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Get included and excluded tags from query parameters
    included_tags = set(filter(None, request.args.get('included_tags', '').split(',')))
    excluded_tags = set(filter(None, request.args.get('excluded_tags', '').split(',')))

    # Start with base query for public events
    query = Event.query.filter(Event.is_public == True)  # noqa: E712

    # Apply tag filters
    if included_tags:
        # Event must have ALL included tags
        for tag in included_tags:
            query = query.filter(Event.tags.contains(tag))
    
    if excluded_tags:
        # Event must have NONE of the excluded tags
        for tag in excluded_tags:
            query = query.filter(~Event.tags.contains(tag))

    # Execute the filtered query
    filtered_events = query.order_by(Event.start_date.desc()).all()

    # Get available tags from filtered events
    available_tags = set()
    for event in filtered_events:
        if event.tags:
            available_tags.update(event.tag_list)

    # Get all tags for excluded ones (they should always be visible)
    all_events = Event.query.filter(
        Event.is_public == True,  # noqa: E712
        Event.tags != None,  # noqa: E711
        Event.tags != ''
    ).all()
    
    all_tags = set()
    for event in all_events:
        if event.tags:
            all_tags.update(event.tag_list)

    # Add excluded tags back to available tags
    available_tags.update(excluded_tags)

    # Sort tags for consistent display
    available_tags = sorted(available_tags)
    
    return render_template('main/index.html',
                         events=filtered_events,
                         all_tags=available_tags,
                         included_tags=included_tags,
                         excluded_tags=excluded_tags,
                         show_reset=bool(included_tags or excluded_tags))

@main.route('/calendar')
def calendar():
    if current_user.is_authenticated:
        # Get all events that are either:
        # 1. User's private events
        # 2. Public events user is attending
        # 3. Public events in user's wishlist
        events = Event.query.filter(
            or_(
                Event.owner_id == current_user.id,  # User's own events
                Event.id.in_(  # Events user is attending
                    db.session.query(EventAttendance.event_id)
                    .filter(EventAttendance.user_id == current_user.id)
                ),
                Event.id.in_(  # Events in user's wishlist
                    db.session.query(EventWishlist.event_id)
                    .filter(EventWishlist.user_id == current_user.id)
                )
            )
        ).order_by(Event.start_date.asc()).all()
    else:
        events = []
    
    return render_template('main/calendar.html', events=events)

@main.route('/search')
def search():
    """Search events and users."""
    query = request.args.get('q', '')
    if not query:
        return render_template('main/search.html', results=None)
    
    # Search events
    events = Event.query.filter(
        Event.is_public == True,  # noqa: E712
        (Event.title.ilike(f'%{query}%') |
         Event.description.ilike(f'%{query}%') |
         Event.location.ilike(f'%{query}%'))
    ).all()
    
    return render_template('main/search.html', results=events, query=query)