from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from .models import Event, EventLike, EventAttendance, EventWishlist
from .forms.event_form import EventForm
from .extensions import db
from datetime import datetime

events = Blueprint('events', __name__)

@events.route('/events')
def list():
    """List all public events and user's private events."""
    if current_user.is_authenticated:
        # Show public events and user's own events
        events = Event.query.filter(
            (Event.is_public == True) |  # noqa: E712
            (Event.owner_id == current_user.id)
        ).order_by(Event.start_date.desc()).all()
    else:
        # Show only public events for non-authenticated users
        events = Event.query.filter_by(is_public=True).order_by(Event.start_date.desc()).all()
    
    # Get tag counts for the sidebar
    tag_counts = Event.get_tag_counts(
        user_id=current_user.id if current_user.is_authenticated else None
    )
    
    return render_template('events/list.html', events=events, tag_counts=tag_counts)

@events.route('/events/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()
    form.current_role.data = current_user.role  # Set the current user's role
    
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            start_time=form.start_time.data,
            is_multiday=form.is_multiday.data,
            end_date=form.end_date.data if form.is_multiday.data else None,
            is_recurring=form.is_recurring.data,
            recurrence_pattern=form.recurrence_pattern.data if form.is_recurring.data else None,
            location=form.location.data,
            venue=form.venue.data,
            is_public=form.is_public.data and current_user.role != 'viewer',  # Extra safety check
            info_link=form.info_link.data,
            tags=form.tags.data,
            owner_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.view', id=event.id))
    
    return render_template('events/form.html', form=form)

@events.route('/events/<int:id>')
def view(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    if not event.is_public and (not current_user.is_authenticated or 
                               current_user.id != event.owner_id and 
                               not current_user.is_admin):
        flash('You do not have permission to view this event.', 'danger')
        return redirect(url_for('events.list'))
    return render_template('events/view.html', event=event)

@events.route('/events/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    if event.owner_id != current_user.id:
        abort(403)
    
    form = EventForm(obj=event)
    form.current_role.data = current_user.role  # Set the current user's role
    
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.start_date = form.start_date.data
        event.start_time = form.start_time.data
        event.is_multiday = form.is_multiday.data
        event.end_date = form.end_date.data if form.is_multiday.data else None
        event.is_recurring = form.is_recurring.data
        event.recurrence_pattern = form.recurrence_pattern.data if form.is_recurring.data else None
        event.location = form.location.data
        event.venue = form.venue.data
        event.is_public = form.is_public.data and current_user.role != 'viewer'  # Extra safety check
        event.info_link = form.info_link.data
        event.tags = form.tags.data
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view', id=id))
    
    return render_template('events/form.html', form=form, event=event)

@events.route('/events/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    
    # Check if user is the owner or admin
    if event.owner_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Delete associated records first
    EventLike.query.filter_by(event_id=id).delete()
    EventAttendance.query.filter_by(event_id=id).delete()
    EventWishlist.query.filter_by(event_id=id).delete()
    
    # Delete the event
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events.list'))

@events.route('/events/<int:id>/like', methods=['POST'])
@login_required
def like(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    
    action = EventLike.toggle(current_user.id, event.id)
    flash(f'Event {action}!', 'success')
    return redirect(request.referrer or url_for('events.view', id=id))

@events.route('/events/<int:id>/likes')
@login_required
def get_likes(id):
    """Get likes for an event."""
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    
    likes = EventLike.query.filter_by(event_id=id).all()
    return jsonify({
        'count': len(likes),
        'users': [{'id': like.user.id, 'username': like.user.username} 
                 for like in likes]
    })

@events.route('/events/<int:id>/attend', methods=['POST'])
@login_required
def attend(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    
    action = EventAttendance.toggle(current_user.id, event.id)
    flash(f'Now {action} the event!', 'success')
    return redirect(request.referrer or url_for('events.view', id=id))

@events.route('/events/<int:id>/wishlist', methods=['POST'])
@login_required
def wishlist(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    
    action = EventWishlist.toggle(current_user.id, event.id)
    flash(f'Event {action} to wishlist!', 'success')
    return redirect(request.referrer or url_for('events.view', id=id))

@events.route('/events/<int:id>/request-promotion', methods=['POST'])
@login_required
def request_promotion(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    
    if event.owner_id != current_user.id:
        abort(403)
    
    if event.is_public:
        flash('Event is already public.', 'warning')
    else:
        event.pending_promotion = True
        db.session.commit()
        flash('Promotion request submitted. An admin will review your request.', 'success')
    
    return redirect(request.referrer or url_for('events.view', id=id))