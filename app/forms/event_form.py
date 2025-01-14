from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, URLField, TimeField, 
    DateField, BooleanField, SelectField, HiddenField
)
from wtforms.validators import DataRequired, Length, URL, Optional, ValidationError
from datetime import date

class EventForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=200)
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(max=2000)
    ])
    start_date = DateField('Start Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[Optional()])
    
    # Conditional fields
    is_multiday = BooleanField('Multi-day Event')
    end_date = DateField('End Date', validators=[Optional()])
    
    is_recurring = BooleanField('Recurring Event')
    recurrence_pattern = SelectField('Repeats', 
        choices=[('', ''), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        validators=[Optional()]
    )
    
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    venue = StringField('Venue', validators=[Optional(), Length(max=200)])
    is_public = BooleanField('Public Event')
    info_link = StringField('Info Link', validators=[Optional(), URL()])
    tags = StringField('Tags (separate with semicolons)', validators=[Optional()])
    current_role = HiddenField('Current Role')  # For validation

    def validate_end_date(self, field):
        if self.is_multiday.data and not field.data:
            raise ValidationError('End date is required for multi-day events')
        if field.data and field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')

    def validate_recurrence_pattern(self, field):
        if self.is_recurring.data and not field.data:
            raise ValidationError('Recurrence pattern is required for recurring events')

    def validate_is_public(self, field):
        if field.data and self.current_role.data == 'viewer':
            raise ValidationError('Viewers can only create private events')