from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Optional

class MemoForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    content = TextAreaField('Content')
    due_date = DateField('Due Date', validators=[Optional()])