from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .forms.auth_forms import LoginForm, RegistrationForm
from .services.user_service import UserService

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = UserService.get_user_by_username(form.username.data)
        if user and UserService.verify_password(user, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid username or password', 'error')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if UserService.get_user_by_username(form.username.data):
            flash('Username already taken.', 'error')
            return render_template('auth/register.html', form=form)
        
        if UserService.get_user_by_email(form.email.data):
            flash('Email already registered.', 'error')
            return render_template('auth/register.html', form=form)
        
        user = UserService.create_user({
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'role': 'viewer'  # Default role for new users
        })
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html') 