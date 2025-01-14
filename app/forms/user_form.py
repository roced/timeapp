from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional

class UserForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    
    password = PasswordField('Password', validators=[
        Optional(),  # Optional for editing users
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    
    role = SelectField('Role', choices=[
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
        ('admin', 'Admin')
    ], validators=[DataRequired()]) 