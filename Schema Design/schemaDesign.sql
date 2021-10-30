
CREATE TABLE "User" (
    "UserID" int   NOT NULL,
    "Name" string   NOT NULL,
    "Email" string   NOT NULL,
    CONSTRAINT "pk_User" PRIMARY KEY (
        "UserID"
     )
);

CREATE TABLE "FavoritesMovie" (
    "FavoritesMovieID" int   NOT NULL,
    "MovieName" string   NOT NULL,
    CONSTRAINT "pk_FavoritesMovie" PRIMARY KEY (
        "FavoritesMovieID"
     )
);

CREATE TABLE "UserFavoritesMovie" (
    "UserFavoritesID" int   NOT NULL,
    "UserID" int   NOT NULL,
    "FavoritesMovieID" int   NOT NULL,
    CONSTRAINT "pk_UserFavoritesMovie" PRIMARY KEY (
        "UserFavoritesID"
     )
);

ALTER TABLE "UserFavoritesMovie" ADD CONSTRAINT "fk_UserFavoritesMovie_UserID" FOREIGN KEY("UserID")
REFERENCES "User" ("UserID");

ALTER TABLE "UserFavoritesMovie" ADD CONSTRAINT "fk_UserFavoritesMovie_FavoritesMovieID" FOREIGN KEY("FavoritesMovieID")
REFERENCES "FavoritesMovie" ("FavoritesMovieID");