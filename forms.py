
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired


class UserRegisterForm(FlaskForm):
    """Form for registring a user"""
    username = StringField("Username:")
    password = PasswordField("Password:")
    email = StringField("Email:")


class UserLoginForm(FlaskForm):
    """Form for User login"""
    username = StringField("Username:")
    password = PasswordField("Password:")
