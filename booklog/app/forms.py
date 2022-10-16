from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Book

# User Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Book Borrow Form
class BorrowForm(FlaskForm):
    book = StringField('Book', validators=[DataRequired()])
    submit = SubmitField('Borrow Book')

# User Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# Book Registration Form
class BookRegistrationForm(FlaskForm):
    book = StringField('Book', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    type = StringField('Book Type', validators=[DataRequired()])
    availibility = StringField('Availibility', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_book(self, book):
        book = Book.query.filter_by(book=book.data).first()
        if book is not None:
            raise ValidationError('Book exists, try a new book')


# Profile Editor Form
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField ('About Me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

# Empty Form
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

# Blog Post Form
class PostForm(FlaskForm):
    post = TextAreaField('What\'s on your mind?', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

# Book Edit Form
class BookEditForm(FlaskForm):
    book = StringField('Book', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    type = StringField('Book Type', validators=[DataRequired()])
    availibility = StringField('Availibility', validators=[DataRequired()])
    submit = SubmitField('Update')

# Borrow Edit Form
class BorrowEditForm(FlaskForm):
    book = StringField('Book', validators=[DataRequired()])
    user = StringField('Username', validators=[DataRequired()]) 
    submit = SubmitField('Update')