import json
import os


from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, flash, redirect, session, g, send_from_directory
from key import SECRET_KEY
from models import connect_db, db, User
from forms import AddUserForm, UserLoginForm
from search_routes import home_search, discover_page
from favorites import display_user_favorites, adding_favorites, removing_favorites
CURR_USER_KEY = "curr_user"

app = Flask(__name__)


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


# ========================= MAIN ROUTE and SEARCH ROUTES ========================================


@app.route("/")
def render_home():
    """Renders home page"""
    return render_template("home.html")


@app.route("/search", methods=["GET"])
def handle_home_search():
    """Handles movie/tvshow search result (by title) only"""
    return home_search()


@app.route("/discover", methods=["GET", "POST"])
def handle_discover_page():
    """Handles discover page"""
    return discover_page()


# =============================== Favorties ROUTES ===============================


@app.route("/favorites", methods=["GET"])
def render_user_favorites():
    """If user is logged in, show current user favorites"""
    return display_user_favorites()


@app.route("/favorites/add/<int:id>/<media_type>", methods=["GET", "POST"])
def handle_adding_favorites(id, media_type):
    """Adds a movie/tvshow to a users favorite list"""
    return adding_favorites(id, media_type)


@app.route("/favorites/remove/<int:id>", methods=["GET", "POST"])
def handle_removing_favorites(id):
    """removes a specified movie from user's favorites"""
    return removing_favorites(id)


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
