CREATE TABLE users
(userid integer, name text, PRIMARY KEY (userid));

CREATE TABLE movies
(movieid integer,title text, PRIMARY KEY (movieid));

CREATE TABLE taginfo
(tagid integer, content text, PRIMARY KEY (tagid));

CREATE TABLE genres
(genreid integer, name text, PRIMARY KEY (genreid));

CREATE TABLE ratings
(userid integer, movieid integer, rating numeric CHECK (rating <= 5), timestamp bigint, FOREIGN KEY (userid) REFERENCES users(userid),FOREIGN KEY (movieid) REFERENCES movies(movieid),
CONSTRAINT ratingunique UNIQUE (userid, movieid)
);

CREATE TABLE tags
(userid integer, movieid integer, tagid integer, timestamp bigint, FOREIGN KEY (userid) REFERENCES users(userid), FOREIGN KEY (movieid) REFERENCES movies(movieid), FOREIGN KEY (tagid) REFERENCES taginfo(tagid));

CREATE TABLE hasagenre
(movieid integer, genreid integer, FOREIGN KEY (movieid) REFERENCES movies(movieid), FOREIGN KEY (genreid) REFERENCES genres(genreid));
    