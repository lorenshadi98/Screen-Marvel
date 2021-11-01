
"""Seed database and create tables"""

from app import db
from models import User, FavoriteMovie, UserFavoriteMovie


db.drop_all()
db.create_all()


db.session.commit()
