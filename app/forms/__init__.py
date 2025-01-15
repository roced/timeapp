# This can be empty or just import the forms
from .auth_forms import LoginForm, RegistrationForm
from .event_form import EventForm
from .user_form import UserForm

__all__ = ['LoginForm', 'RegistrationForm', 'EventForm', 'UserForm']
