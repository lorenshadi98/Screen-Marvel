import json
import os

from flask import Flask, render_template, request, flash, redirect, session, g, send_from_directory
from sqlalchemy.exc import IntegrityError
import requests
from key import API_KEY

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

BASE_API_URL = "https://www.omdbapi.com/"


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     os.environ.get('DATABASE_URL', 'postgresql:///screen-marvel'))

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def render_home():
    # movie = {
    #     "s": "hunger games",
    #     "apikey": API_KEY,
    #     "page": "1"
    # }
    # response = requests.get(BASE_API_URL, params=movie)
    # jprint(response.json())

    return render_template("home.html")


@app.route("/search")
def handle_home_search():
    return "Search recieved"
