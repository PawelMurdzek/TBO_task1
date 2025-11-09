# Form imports
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp


# Flask forms (wtforms) allow you to easily create forms in this format:
class CreateCustomer(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=1, max=64, message='Name must be between 1 and 64 characters'),
        Regexp(r'^[a-zA-Z\s\-\.]+$', message='Name can only contain letters, spaces, hyphens and dots')
    ])  
    city = StringField('City', validators=[
        DataRequired(message='City is required'),
        Length(min=1, max=64, message='City must be between 1 and 64 characters'),
        Regexp(r'^[a-zA-Z\s\-\.]+$', message='City can only contain letters, spaces, hyphens and dots')
    ])
    age = IntegerField('Age', validators=[
        DataRequired(message='Age is required'),
        NumberRange(min=0, max=150, message='Age must be between 0 and 150')
    ])
    submit = SubmitField('Create Customer')
