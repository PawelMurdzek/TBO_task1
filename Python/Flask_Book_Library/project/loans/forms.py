# Form imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp


# Flask forms (wtforms) allow you to easily create forms in format:
class CreateLoan(FlaskForm):
    customer_name = StringField('Customer Name', validators=[
        DataRequired(message='Customer name is required'),
        Length(min=1, max=64, message='Customer name must be between 1 and 64 characters'),
        Regexp(r'^[a-zA-Z\s\-\.]+$', message='Customer name can only contain letters, spaces, hyphens and dots')
    ])
    book_name = StringField('Book Name', validators=[
        DataRequired(message='Book name is required'),
        Length(min=1, max=64, message='Book name must be between 1 and 64 characters'),
        Regexp(r'^[a-zA-Z0-9\s\-\.,!?\'"]+$', message='Book name contains invalid characters')
    ])
    loan_date = DateField('Loan Date', format='%Y-%m-%d', validators=[DataRequired(message='Loan date is required')])
    return_date = DateField('Return Date', format='%Y-%m-%d', validators=[DataRequired(message='Return date is required')])

    # Fields for capturing original book details
    original_author = StringField('Original Author', validators=[
        DataRequired(message='Author is required'),
        Length(max=64, message='Author name must be at most 64 characters'),
        Regexp(r'^[a-zA-Z\s\-\.]+$', message='Author name can only contain letters, spaces, hyphens and dots')
    ])
    original_year_published = IntegerField('Original Year Published', validators=[
        DataRequired(message='Year is required'),
        NumberRange(min=1000, max=2100, message='Year must be between 1000 and 2100')
    ])
    original_book_type = StringField('Original Book Type', validators=[DataRequired(message='Book type is required')])

    submit = SubmitField('Create Loan')

