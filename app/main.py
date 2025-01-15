from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from .models import Event
from .services.tag_service import TagService
from .services.event_service import EventService
from datetime import datetime, UTC

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Show homepage with filtered events."""
    # Get included and excluded tags from query parameters
    included_tags = set(filter(None, request.args.get('included_tags', '').split(';')))
    excluded_tags = set(filter(None, request.args.get('excluded_tags', '').split(';')))

    # Use TagService to get filtered events
    filtered_events = TagService.filter_events_by_tags(
        included_tags, 
        excluded_tags,
        current_user.id if current_user.is_authenticated else None
    )

    # Get available tags from filtered events
    available_tags = set()
    for event in filtered_events:
        if event.tags:
            available_tags.update(event.tag_list)

    # Add excluded tags back to available tags (they should always be visible)
    available_tags.update(excluded_tags)

    return render_template('main/index.html',
                         events=filtered_events,
                         all_tags=sorted(available_tags),
                         included_tags=included_tags,
                         excluded_tags=excluded_tags,
                         show_reset=bool(included_tags or excluded_tags))

@main.route('/calendar')
def calendar():
    """Show calendar view of events."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
        
    events = EventService.get_calendar_events(
        user_id=current_user.id if current_user.is_authenticated else None
    )
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