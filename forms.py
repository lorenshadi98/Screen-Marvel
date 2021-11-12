
from re import L
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired


class AddUserForm(FlaskForm):
    """Form for registring a user"""
    username = StringField("Username:")
    password = PasswordField("Password:")
    email = StringField("Email:")
    image_url = StringField("Profile Image:")


class UserLoginForm(FlaskForm):
    """Form for user login"""
    username = StringField("Username:")
    password = PasswordField("Password:")


class DiscoverMovieForm(FlaskForm):
    """Form for user movie discover"""
    movie_genre = SelectField("Genre", choices=[(28, "Action"), (12, "Adventure"), (
        16, "Animation"), (35, "Comedy"), (80, "Crime"), (99, "Documentary"),
        (18, "Drama"), (10751, "Family"), (14, "Fantasy"), (36, "History"),
        (27, "Horror"), (10402, "Music"), (9648, "Mystery"), (10749, "Romance"),
        (878, "Science Fiction"), (10770,
                                   "TV Movie"), (53, "Thriller"), (10752, "War"),
        (37, "Western")], coerce=int)
