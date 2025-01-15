from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from .services.user_service import UserService
from .services.event_service import EventService
from .forms.user_form import UserForm
from .extensions import db
import csv
from io import StringIO

admin = Blueprint('admin', __name__)

@admin.before_request
def require_admin():
    if not current_user.is_authenticated or current_user.role != 'admin':
        abort(403)

@admin.route('/admin')
@admin.route('/admin/')
@login_required
def index():
    """Redirect to admin dashboard."""
    return redirect(url_for('admin.dashboard'))

@admin.route('/admin/dashboard')
@login_required
def dashboard():
    """Admin dashboard with statistics."""
    stats = {
        'total_users': UserService.get_user_count(),
        'total_events': EventService.get_event_count(),
        'pending_promotions': EventService.get_pending_promotions_count(),
        'recent_events': EventService.get_recent_events(limit=5)
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin.route('/admin/users')
@login_required
def manage_users():
    """List all users."""
    users = UserService.get_all_users()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/events')
@login_required
def manage_events():
    """List all events."""
    events = EventService.get_all_events()
    return render_template('admin/events.html', events=events)

@admin.route('/admin/promotions')
@login_required
def manage_promotions():
    """List events pending promotion."""
    events = EventService.get_pending_promotions()
    return render_template('admin/promotions.html', events=events)

@admin.route('/admin/import', methods=['GET', 'POST'])
@login_required
def import_events():
    """Handle CSV file upload."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded.', 'error')
            return redirect(url_for('admin.import_events'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('admin.import_events'))
        
        if not file.filename.endswith('.csv'):
            flash('Only CSV files are allowed.', 'error')
            return redirect(url_for('admin.import_events'))
        
        try:
            stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_data = csv.DictReader(stream)
            success_count = EventService.bulk_create_events(csv_data, current_user.id)
            flash(f'Successfully imported {success_count} events.', 'success')
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
        
        return redirect(url_for('admin.manage_events'))
    
    return render_template('admin/import.html')

@admin.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """Edit a user."""
    user = UserService.get_user_by_id(id)
    if not user:
        abort(404)
    
    form = UserForm(obj=user)
    if form.validate_on_submit():
        UserService.update_user(user, {
            'username': form.username.data,
            'email': form.email.data,
            'role': form.role.data
        })
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/user_form.html', form=form, user=user)

@admin.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    """Delete a user."""
    user = UserService.get_user_by_id(id)
    if not user:
        abort(404)
    if user.id == current_user.id:
        flash('Cannot delete yourself.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    UserService.delete_user(user)
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/events/<int:id>/approve', methods=['POST'])
@login_required
def approve_promotion(id):
    """Approve an event promotion request."""
    if EventService.approve_promotion(id):
        flash('Event promotion approved.', 'success')
    else:
        flash('Failed to approve promotion.', 'error')
    return redirect(url_for('admin.manage_promotions'))

@admin.route('/admin/events/<int:id>/reject', methods=['POST'])
@login_required
def reject_promotion(id):
    """Reject an event promotion request."""
    if EventService.reject_promotion(id):
        flash('Event promotion rejected.', 'success')
    else:
        flash('Failed to reject promotion.', 'error')
    return redirect(url_for('admin.manage_promotions')) 