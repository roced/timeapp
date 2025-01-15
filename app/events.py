from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .models import Event
from .forms.event_form import EventForm
from .services.event_service import EventService

events = Blueprint('events', __name__)

@events.route('/events/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()
    form.current_role.data = current_user.role
    
    if form.validate_on_submit():
        event = EventService.create_event({
            'title': form.title.data,
            'description': form.description.data,
            'start_date': form.start_date.data,
            'start_time': form.start_time.data,
            'is_multiday': form.is_multiday.data,
            'end_date': form.end_date.data,
            'is_recurring': form.is_recurring.data,
            'recurrence_pattern': form.recurrence_pattern.data,
            'location': form.location.data,
            'venue': form.venue.data,
            'is_public': form.is_public.data and current_user.role != 'viewer',
            'info_link': form.info_link.data,
            'tags': form.tags.data
        }, current_user.id)
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.view', id=event.id))
    
    return render_template('events/form.html', form=form)

@events.route('/events/<int:id>')
def view(id):
    """View a single event."""
    event = EventService.get_event_by_id(
        id, 
        current_user.id if current_user.is_authenticated else None
    )
    if not event:
        abort(404)
    return render_template('events/view.html', event=event)

@events.route('/events/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an event."""
    event = EventService.get_event_by_id(id, current_user.id)
    if not event or event.owner_id != current_user.id:
        abort(403)
    
    form = EventForm(obj=event)
    form.current_role.data = current_user.role
    
    if form.validate_on_submit():
        event = EventService.update_event(event, {
            'title': form.title.data,
            'description': form.description.data,
            'start_date': form.start_date.data,
            'start_time': form.start_time.data,
            'is_multiday': form.is_multiday.data,
            'end_date': form.end_date.data,
            'is_recurring': form.is_recurring.data,
            'recurrence_pattern': form.recurrence_pattern.data,
            'location': form.location.data,
            'venue': form.venue.data,
            'is_public': form.is_public.data and current_user.role != 'viewer',
            'info_link': form.info_link.data,
            'tags': form.tags.data
        })
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view', id=event.id))
        
    return render_template('events/form.html', form=form, event=event)

@events.route('/events/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete an event."""
    event = EventService.get_event_by_id(id, current_user.id)
    if not event or event.owner_id != current_user.id:
        abort(403)
        
    EventService.delete_event(event)
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('main.index'))

@events.route('/events/<int:id>/request-promotion', methods=['POST'])
@login_required
def request_promotion(id):
    """Request promotion for an event."""
    event = EventService.get_event_by_id(id, current_user.id)
    if not event or event.owner_id != current_user.id:
        abort(403)
    
    if EventService.request_promotion(id, current_user.id):
        flash('Promotion request submitted successfully!', 'success')
    else:
        flash('Failed to submit promotion request.', 'error')
    
    return redirect(url_for('events.view', id=id))