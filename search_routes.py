from queries import handle_query_by_title, handle_tmdb_discover
from flask import render_template, request, flash, redirect
from forms import DiscoverMovieForm


def home_search():
    """Handles movie/tvshow search result (by title) only"""
    parsed_result = handle_query_by_title(request.args.get("movie_title"))

    if len(parsed_result["results"]) > 0:
        return render_template("home.html", search_result=parsed_result["results"])
    else:
        flash("No content found!", 'danger')
        return redirect("/")


def discover_page():
    form = DiscoverMovieForm()
    movie_genreID = '28'
    discover_result = handle_tmdb_discover(movie_genreID)

    if form.validate_on_submit():
        movie_genreID = form.movie_genre.data
        discover_result = handle_tmdb_discover(movie_genreID)

        return render_template("movie/discover.html", discover_result=discover_result["results"], form=form)
    else:
        return render_template("movie/discover.html", discover_result=discover_result["results"], form=form)
