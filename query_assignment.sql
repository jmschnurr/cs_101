--1. total number of movies for each genre
-- “query1” which has two attributes: “name” attribute is a list of genres, and “moviecount”

CREATE TABLE query1 AS(
select genres.name, COUNT(hasagenre.movieid) as moviecount
FROM hasagenre
INNER JOIN genres ON hasagenre.genreid=genres.genreid
GROUP BY genres.name);

--2. average rating per genre 
-- “name” attribute is a list of all genres, and “rating” attribute is a list of average rating per genre.

CREATE TABLE query2 AS(
select genres.name, AVG(ratings.rating) as rating
FROM ratings
	INNER JOIN hasagenre
	ON ratings.movieid = hasagenre.movieid 
	INNER JOIN genres
	ON genres.genreid = hasagenre.genreid
	GROUP BY genres.name);
	
	
--3. return the movies which have at least 10 ratings
-- “query3” which has two attributes: “title” is a list of movie titles, and “CountOfRatings” 

CREATE TABLE query3 AS(
select movies.title, COUNT(ratings.rating) as countofratings
FROM ratings
	INNER JOIN movies ON ratings.movieid = movies.movieid
	GROUP BY movies.title
	having COUNT(ratings.rating) >= 10);
	
-- 4. all “Comedy” movies, including movieid and title
-- “query4” which has two attributes: “movieid” is a list of movie ids, and “title” 

CREATE TABLE query4 AS(
SELECT movies.movieid, movies.title
FROM genres
	INNER JOIN hasagenre 
	ON genres.genreid = hasagenre.genreid
	INNER JOIN movies 
	ON hasagenre.movieid = movies.movieid
	where genres.name = 'Comedy');
	
-- 5. Write a SQL query to return the average rating per movie.
-- two attributes: “title” is a list of movie titles, and “average” is a list of the average rating 

CREATE TABLE query5 AS(
select movies.title, AVG(ratings.rating) as average
FROM ratings
	INNER JOIN movies
	ON ratings.movieid = movies.movieid 
	GROUP BY movies.title);

-- 6. Write a SQL query to return the average rating for all “Comedy” movies. 
--Your query result should be saved in a table called “query6” which has one attribute: “average”

CREATE TABLE query6 AS(
select AVG(ratings.rating) as average
FROM ratings
	INNER JOIN hasagenre
	ON ratings.movieid = hasagenre.movieid 
	INNER JOIN genres
	ON genres.genreid = hasagenre.genreid
	GROUP BY genres.name
		having genres.name = 'Comedy');
	
-- 7. return the average rating for all movies and each of these movies is both “Comedy” and “Romance”.

CREATE TABLE query7 AS(
SELECT AVG(rating) as average
FROM
	((select ratings.movieid
	FROM ratings
		INNER JOIN hasagenre
		ON ratings.movieid = hasagenre.movieid 
		INNER JOIN genres
		ON genres.genreid = hasagenre.genreid
		WHERE genres.name = 'Comedy'
intersect 
	select ratings.movieid
	FROM ratings
		INNER JOIN hasagenre
		ON ratings.movieid = hasagenre.movieid 
		INNER JOIN genres
		ON genres.genreid = hasagenre.genreid
		WHERE genres.name = 'Romance') as T
		join ratings
  		on T.movieid = ratings.movieid) as B);
		
-- 8. Write a SQL query to return the average rating for all movies and each of these movies is “Romance” but not “Comedy”.

CREATE TABLE query8 AS(
SELECT AVG(rating) as average
FROM
	((select ratings.movieid
	FROM ratings
		INNER JOIN hasagenre
		ON ratings.movieid = hasagenre.movieid 
		INNER JOIN genres
		ON genres.genreid = hasagenre.genreid
		WHERE genres.name = 'Romance'
except
	select ratings.movieid
	FROM ratings
		INNER JOIN hasagenre
		ON ratings.movieid = hasagenre.movieid 
		INNER JOIN genres
		ON genres.genreid = hasagenre.genreid
		WHERE genres.name = 'Comedy') as T
		join ratings
  		on T.movieid = ratings.movieid) as B);

-- 9. Find all movies that are rated by a user such that the userId is equal to v1.
CREATE TABLE query9 AS(
select ratings.movieid, ratings.rating
FROM ratings
where ratings.userid = :v1);
