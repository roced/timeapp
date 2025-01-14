from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, URLField, TimeField, 
    DateField, BooleanField, SelectField, HiddenField
)
from wtforms.validators import DataRequired, Length, URL, Optional, ValidationError
from datetime import date
from ..models import User

class EventForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=128)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=2000)
    ])
    info_link = URLField('External Link', validators=[
        Optional(),
        URL()
    ])
    start_date = DateField('Start Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    
    # Conditional fields
    is_multiday = BooleanField('Multi-day Event')
    end_date = DateField('End Date', validators=[Optional()])
    
    is_recurring = BooleanField('Recurring Event')
    recurrence_pattern = SelectField('Repeats', 
        choices=[('', ''), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        validators=[Optional()]
    )
    
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    venue = StringField('Venue', validators=[Optional(), Length(max=128)])
    tags = StringField('Tags (comma-separated)', validators=[Optional(), Length(max=256)])
    
    is_public = BooleanField('Public Event')
    current_role = HiddenField('Current Role')  # For validation

    def validate_end_date(self, field):
        if self.is_multiday.data and field.data:
            if field.data < self.start_date.data:
                raise ValidationError('End date must be after start date')

    def validate_is_public(self, field):
        if field.data and self.current_role.data == 'viewer':
            raise ValidationError('Viewers can only create private events')

    def validate_recurrence_pattern(self, field):
        if self.is_recurring.data and not field.data:
            raise ValidationError('Recurrence pattern is required for recurring events') 