# Form imports
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp


# Flask forms (wtforms) allow you to easily create forms in format:
class CreateBook(FlaskForm):
    name = StringField('Book Name', validators=[
        DataRequired(message='Book name is required'),
        Length(min=1, max=64, message='Book name must be between 1 and 64 characters'),
        Regexp(r'^[a-zA-Z0-9\s\-\.,!?\'"]+$', message='Book name contains invalid characters')
    ])
    author = StringField('Author', validators=[
        Length(max=64, message='Author name must be at most 64 characters'),
        Regexp(r'^[a-zA-Z\s\-\.]+$', message='Author name can only contain letters, spaces, hyphens and dots')
    ])
    year_published = IntegerField('Year Published', validators=[
        DataRequired(message='Year is required'),
        NumberRange(min=1000, max=2100, message='Year must be between 1000 and 2100')
    ])
    book_type = SelectField('Book Type', choices=[('2days', 'Up to 2 days'), ('5days', 'Up to 5 days'), ('10days', 'Up to 10 days')], validators=[DataRequired()])
    submit = SubmitField('Create Book')
