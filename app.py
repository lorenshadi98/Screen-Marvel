import json
import os
import requests


from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, request, flash, redirect, session, g, send_from_directory, url_for
from key import API_KEY
from models import connect_db, db, User, FavoriteMovie
from forms import AddUserForm, EditUserForm, UserLoginForm
CURR_USER_KEY = "curr_user"

app = Flask(__name__)

BASE_API_URL = "https://www.omdbapi.com/"


# ============================= DATABASE AND APP CONFIG ==============================

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///screen-marvel'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
connect_db(app)


# ====================== favicon loading page==============================


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# ============================= Movie query helper functions ==============================

def handle_query_by_title(query):
    """Handles the main page movie query by title only"""
    user_movie_search = {
        "s": query,
        "apikey": API_KEY,
        "page": '1'
    }
    response = requests.get(BASE_API_URL, params=user_movie_search)
    data = response.text
    parsed_result = json.loads(data)
    return parsed_result


def handle_query_by_imdbID(imdbID):
    """Handles API query by IMBDID in order to save database space"""
    imdb_movie_search = {
        "i": imdbID,
        "apikey": API_KEY
    }
    response = requests.get(BASE_API_URL, params=imdb_movie_search)
    data = response.text
    parsed_result = json.loads(data)
    return parsed_result

# ============================= USER SESSION functions ==============================


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

# ========================= MAIN ROUTE and SEARCH ROUTE ========================================


@app.route("/")
def render_home():
    """Renders home page"""
    return render_template("home.html")


@app.route("/search", methods=["GET"])
def handle_home_search():
    """Handles movie search result (by title) only"""
    parsed_result = handle_query_by_title(request.args.get("movie_title"))

    if parsed_result["Response"] == "True":
        return render_template("movie/search.html", url_list=parsed_result["Search"])
    else:
        flash("No movie found!", 'danger')
        return redirect("/")

# =============================== USER ROUTES ===============================


@app.route("/account", methods=["GET"])
def render_user_details():
    if g.user:
        return render_template("users/show.html")
    else:
        flash("Cannot view this page")
        return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def handle_user_signup():
    """Handles user signup. 
    If the user is signed in they are redirected back to home.
    If the signup form is insecure or invalid redirect to the form again for another attempt.
    If the information is completed and valid the user is signed up and then logged in.

    """
    if g.user:
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


@app.route("/login", methods=["GET", "POST"])
def handle_login():
    """Handles user signin. IF user is already signed in they are redirected to home.
        If the user credientials are correct, they are logged in. Otherwise they try again.
    """
    if g.user:
        return redirect("/")
    else:
        form = UserLoginForm()
        if form.validate_on_submit():
            user = User.authenticate(
                username=form.username.data, password=form.password.data)
            if user:
                do_login(user)
                return redirect("/")
            else:
                flash("Invalid username or password", "danger")
                return render_template("users/login.html", form=form)
        else:
            return render_template("users/login.html", form=form)


@app.route('/logout', methods=["GET"])
def handle_logout():
    """Handles user logout."""
    if g.user:
        do_logout()
        return redirect("/")
    else:
        return redirect("/")

# =============================== Favorties ROUTES ===============================


@app.route("/favorites", methods=["GET"])
def render_user_favorites():
    """If user is logged in, show current user favorites"""
    if not g.user:
        flash("Cannot load favorites, please login first", "danger")
        return redirect("/login")
    else:
        favorites_list = []
        for favorite in g.user.favorites:
            favorites_list.append(handle_query_by_imdbID(favorite.imdbID))

        return render_template("users/favorites.html", url_list=favorites_list)


@app.route("/favorites/add/<imdbID>", methods=["GET", "POST"])
def handle_adding_favorites(imdbID):
    """Adds a movie to a users favorite list"""

    if not g.user:
        flash("You must be logged in first to add a favorite", "warning")
        return redirect("/login")
    else:
        # Creates favorite movie instance with minimal information to save storage. We
        # let the API to handle the rest of the data of the favorited movie.

        movie = FavoriteMovie(imdbID=imdbID, user_id=g.user.id)
        db.session.add(movie)
        db.session.commit()

        flash("Movie added to Favorites!", "success")
        return redirect("/favorites")


@app.route("/favorites/remove/<imdbID>", methods=["GET", "POST"])
def handle_removing_favorites(imdbID):
    """removes a specified movie from user's favorites"""
    if not g.user:
        flash("You must be logged in first to remove a favorite", "warning")
        return redirect("/login")
    else:
        movie = FavoriteMovie.query.filter(
            FavoriteMovie.imdbID == imdbID).first()
        # removes the movie from the favorites list and then removes the instance from
        # the database.
        g.user.favorites.remove(movie)
        db.session.delete(movie)
        db.session.commit()
        return redirect("/favorites")


@app.after_request
def add_header(req):
    ##############################################################################
    # Turn off all caching in Flask
    #   (useful for dev; in production, this kind of stuff is typically
    #   handled elsewhere) #
    # https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
