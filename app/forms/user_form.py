from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('viewer', 'Viewer'), ('editor', 'Editor'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Save Changes') 