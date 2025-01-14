from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from .models import User, Event, Memo
from .forms.user_form import UserForm
from .extensions import db
from functools import wraps
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, UTC
from sqlalchemy import or_

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin/')
@login_required
@admin_required
def index():
    """Admin dashboard index."""
    user_count = User.query.count()
    event_count = Event.query.count()
    memo_count = Memo.query.count()
    pending_promotions = Event.query.filter_by(pending_promotion=True).count()
    
    return render_template('admin/index.html', 
                         user_count=user_count,
                         event_count=event_count,
                         memo_count=memo_count,
                         pending_promotions=pending_promotions)

@admin.route('/admin/manage/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/user_form.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/user_form.html', form=form)

@admin.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    
    form = UserForm(obj=user)
    if form.validate_on_submit():
        username_exists = User.query.filter(User.username == form.username.data, 
                                         User.id != user_id).first()
        if username_exists:
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, user=user)
        
        email_exists = User.query.filter(User.email == form.email.data, 
                                       User.id != user_id).first()
        if email_exists:
            flash('Email already registered.', 'danger')
            return render_template('admin/user_form.html', form=form, user=user)
        
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        user.role = form.role.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/user_form.html', form=form, user=user)

@admin.route('/admin/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_role(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    
    new_role = request.form.get('role')
    if new_role not in ['viewer', 'editor', 'admin']:
        abort(400)
    
    user.role = new_role
    db.session.commit()
    flash(f'Role updated for {user.username}', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('You cannot delete yourself!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been deleted', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/promotions')
@login_required
@admin_required
def manage_promotions():
    pending_events = Event.query.filter_by(pending_promotion=True).order_by(Event.created_at.desc()).all()
    return render_template('admin/manage_promotions.html', events=pending_events)

@admin.route('/admin/promotions/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_promotion(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    
    event.is_public = True
    event.pending_promotion = False
    db.session.commit()
    flash(f'Event "{event.title}" has been made public.', 'success')
    return redirect(url_for('admin.manage_promotions'))

@admin.route('/admin/promotions/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_promotion(id):
    event = db.session.get(Event, id)
    if not event:
        abort(404)
    
    event.pending_promotion = False
    db.session.commit()
    flash(f'Promotion request for "{event.title}" has been rejected.', 'warning')
    return redirect(url_for('admin.manage_promotions')) 