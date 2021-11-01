import json
import os
import requests


from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, request, flash, redirect, session, g, send_from_directory
from key import API_KEY
from models import connect_db, db, User, FavoriteMovie, UserFavoriteMovie
from forms import AddUserForm, EditUserForm
CURR_USER_KEY = "curr_user"

app = Flask(__name__)

BASE_API_URL = "https://www.omdbapi.com/"


# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///screen-marvel'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
connect_db(app)


# ====================== favicon and helper functions ==============================


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def handle_movie_query(query):
    user_movie_search = {
        "s": query,
        "apikey": API_KEY,
        "page": '1'
    }
    response = requests.get(BASE_API_URL, params=user_movie_search)
    data = response.text
    parsed_result = json.loads(data)
    return parsed_result


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# ========================= MAIN ROUTES ========================================


@app.route("/")
def render_home():

    return render_template("home.html")


@app.route("/search", methods=["GET"])
def handle_home_search():
    parsed_result = handle_movie_query(request.args.get("movie_title"))

    if parsed_result["Response"] == "True":
        return render_template("movie/search.html", url_list=parsed_result["Search"])
    else:
        flash("No movie found!", 'danger')
        return redirect("/")

# =============================== USER ROUTES ===============================


@app.route("/signup", methods=["GET", "POST"])
def handle_user_signup():
    if g.user in session:
        return redirect("/")
    else:
        form = AddUserForm()
        if form.validate_on_submit():
            try:
                user = User.signup(username=form.username.data, email=form.email.data,
                                   password=form.password.data, image_url=form.image_url.data)
                db.session.commit()
            except IntegrityError:
                flash("Username taken!", "danger")
                return render_template('users/signup.html', form=form)

            do_login(user)
            return redirect("/")
        else:
            return render_template('users/signup.html', form=form)


@app.route('/logout', methods=["GET"])
def handle_logout():
    if g.user:
        do_logout()
        return redirect("/")
    else:
        flash("Logout Unsuccessful", "danger")
        return redirect("/")


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere) #
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
