import json
import os
import requests


from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, request, flash, redirect, session, g, send_from_directory, url_for
from key import API_KEY, SECRET_KEY, TMDB_API_KEY
from models import connect_db, db, User, FavoriteMovie
from forms import AddUserForm, EditUserForm, UserLoginForm, DiscoverMovieForm
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', SECRET_KEY)
connect_db(app)


# ====================== favicon loading page==============================


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def jsonpretty(parsed_result):
    print(json.dumps(parsed_result, indent=4, sort_keys=True))
    return "Results printed"

# ============================= Movie query helper functions ==============================


def handle_query_by_title(query):
    """Handles the main page movie query by title only"""
    # Sample query: https://api.themoviedb.org/3/search/movie?
    # api_key=18844f2c950dd9b8f53a0beff301a9b8&language=en-US&query=
    # hunger%20games&page=1&include_adult=false
    user_movie_search = {
        "api_key": TMDB_API_KEY,
        "Language": "en-US",
        "query": query,
        "include_adult": "false"
    }
    response = requests.get(
        "https://api.themoviedb.org/3/search/multi", params=user_movie_search)
    data = response.text
    parsed_result = json.loads(data)
    return parsed_result


def handle_search_by_id(content_id, content_type):
    """Searches database by id depending on content type"""
    print("RECIEVED CONTENT TYPE IS ________________",
          content_type, "id is", content_id)
    if content_type == "movie":
        print("Entered movie")
        movie_id_search = {
            "api_key": TMDB_API_KEY
        }
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{content_id}", params=movie_id_search)
        data = response.text
        parsed_result = json.loads(data)
        jsonpretty(parsed_result)
        return parsed_result
    elif content_type == "tv":
        print("Entered tv")
        tv_id_search = {
            "api_key": TMDB_API_KEY
        }

        response = requests.get(
            f"https://api.themoviedb.org/3/tv/{content_id}", params=tv_id_search)
        data = response.text
        parsed_result = json.loads(data)
        jsonpretty(parsed_result)
        return parsed_result


def handle_tmdb_discover(genreID):
    """Generates a discover query result for the user's most favorited genre"""
    tmdb_discover_search = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": '1',
        "with_genres": genreID
    }
    response = requests.get(
        "https://api.themoviedb.org/3/discover/movie", params=tmdb_discover_search)
    data = response.text
    parsed_result = json.loads(data)
    return parsed_result


# ========================= MAIN ROUTE and SEARCH ROUTES ========================================


@app.route("/")
def render_home():
    """Renders home page"""
    return render_template("home.html")


@app.route("/search", methods=["GET"])
def handle_home_search():
    """Handles movie/tvshow search result (by title) only"""
    parsed_result = handle_query_by_title(request.args.get("movie_title"))

    if len(parsed_result["results"]) > 0:
        return render_template("home.html", search_result=parsed_result["results"])
    else:
        flash("No content found!", 'danger')
        return redirect("/")


@app.route("/discover", methods=["GET", "POST"])
def handle_discover_page():
    form = DiscoverMovieForm()
    movie_genreID = '28'
    discover_result = handle_tmdb_discover(movie_genreID)

    if form.validate_on_submit():
        movie_genreID = form.movie_genre.data
        discover_result = handle_tmdb_discover(movie_genreID)

        return render_template("movie/discover.html", discover_result=discover_result["results"], form=form)
    else:
        return render_template("movie/discover.html", discover_result=discover_result["results"], form=form)


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

            favorites_list.append(handle_search_by_id(
                favorite.content_id, favorite.content_type))

        return render_template("users/favorites.html", favorites_list=favorites_list)


@app.route("/favorites/add/<int:id>/<media_type>", methods=["GET", "POST"])
def handle_adding_favorites(id, media_type):
    """Adds a movie/tvshow to a users favorite list"""
    # get movie id. Query movie/tvshow id for imdb id. then add that favorite there.
    if not g.user:
        flash("You must be logged in first to add a favorite", "warning")
        return redirect("/login")
    else:
        # Creates favorite movie instance with minimal information to save storage. We
        # let the API to handle the rest of the data of the favorited movie.

        # checks and handles movie duplication.
        foundMovie = FavoriteMovie.query.filter(
            FavoriteMovie.content_id == id).first()

        if foundMovie:
            flash("Movie already in your favorites!", "warning")
            return redirect("/favorites")
        else:
            movie = FavoriteMovie(
                content_id=id, content_type=media_type, user_id=g.user.id)
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
