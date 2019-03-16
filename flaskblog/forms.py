from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,IntegerField,RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username=StringField('Username',
                            validators=[DataRequired(), Length(min=2,max=20)])
    email=StringField('Email',
                            validators=[DataRequired(), Email(message="invalid email address")])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password',message="passwords must match")])
    submit=SubmitField('Sign Up')

    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email=StringField('Email',
                            validators=[DataRequired(), Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')

class RequestResetForm(FlaskForm):
    email=StringField('Email',
                            validators=[DataRequired(), Email()])
    submit=SubmitField('Request Reset Password')
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email. Please register first.')

class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password',message="passwords must match")])
    submit=SubmitField('Reset Password')

class AddPatient(FlaskForm):
    firstName = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastName = StringField('Last Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    age = StringField('Age',
                            validators=[DataRequired(), Length(min=2, max=20)])
    gender = RadioField('Gender', validators=[DataRequired()], choices = [('M','Male'),('F','Female')], default='M')
    latitude = StringField('Latitude')
    longitude = StringField('Longitude')
    file = FileField('Upload File', validators=[DataRequired(), FileAllowed(['nii.gz', 'nii', 'gz', 'jpg','csv'])])
    submit = SubmitField('Add')

