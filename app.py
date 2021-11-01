import json
import os

from flask import Flask, render_template, request, flash, redirect, session, g, send_from_directory
from sqlalchemy.exc import IntegrityError
import requests
from key import API_KEY

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

BASE_API_URL = "https://www.omdbapi.com/"


# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     os.environ.get('DATABASE_URL', 'postgresql:///screen-marvel'))

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")


def handle_movie_query(query):
    user_movie_search = {
        "s": query,
        "apikey": API_KEY
    }
    response = requests.get(BASE_API_URL, params=user_movie_search)
    data = response.text
    parsed_result = json.loads(data)
    return parsed_result


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


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
