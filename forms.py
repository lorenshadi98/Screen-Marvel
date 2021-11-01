
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired


class AddUserForm(FlaskForm):
    """Form for registring a user"""
    username = StringField("Username:")
    password = PasswordField("Password:")
    email = StringField("Email:")
    image_url = StringField("Profile Image:")


class EditUserForm(FlaskForm):
    """Form for User login"""
    username = StringField("Username:")
    email = StringField("Email:")
    image_url = StringField("Profile Image:")
