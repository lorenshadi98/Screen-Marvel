from flask import render_template, flash, redirect, g
from queries import handle_search_by_id
from models import FavoriteMovie, db


def display_user_favorites():
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


def adding_favorites(id, media_type):
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


def removing_favorites(id):
    """removes a specified movie from user's favorites"""
    if not g.user:
        flash("You must be logged in first to remove a favorite", "warning")
        return redirect("/login")
    else:
        movie = FavoriteMovie.query.filter(
            FavoriteMovie.content_id == id).first()
        # removes the movie from the favorites list and then removes the instance from
        # the database.
        g.user.favorites.remove(movie)
        db.session.delete(movie)
        db.session.commit()
        return redirect("/favorites")
