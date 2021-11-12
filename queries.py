import requests
from key import TMDB_API_KEY
import json


def handle_query_by_title(query):
    """Handles the main page movie query by title only"""

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

    if content_type == "movie":
        print("Entered movie")
        movie_id_search = {
            "api_key": TMDB_API_KEY
        }
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{content_id}", params=movie_id_search)
        data = response.text
        parsed_result = json.loads(data)

        return parsed_result
    elif content_type == "tv":

        tv_id_search = {
            "api_key": TMDB_API_KEY
        }
        response = requests.get(
            f"https://api.themoviedb.org/3/tv/{content_id}", params=tv_id_search)
        data = response.text
        parsed_result = json.loads(data)
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
