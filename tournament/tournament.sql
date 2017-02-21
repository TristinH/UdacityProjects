-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Deletes previous database to try new schema.
DROP DATABASE IF EXISTS tournament;
-- Creates the database for the tournamnet.
CREATE DATABASE tournament;

-- Change into tournament database.
\c tournament;

-- Creates a table to store player information.
-- id is a unique identifier for each player,
-- name is the submitted player's name.
CREATE TABLE Players (
		id serial PRIMARY KEY,
		name text
	);

-- Creates a table to track match results.
-- id is a unique identifier for each match,
-- winner is the id of the winning player,
-- loser is the id of the losing player.
CREATE TABLE Matches (
		id serial PRIMARY KEY,
		winner integer,
		loser integer
	);

-- Creates a view of all the players in 
-- descending order of number of wins.
CREATE VIEW PlayerOrder as 
	SELECT Players.id,
		   count(Matches.winner) as wins
	FROM Players
	LEFT JOIN Matches
	ON Matches.winner = Players.id
	GROUP BY Players.id
	ORDER BY wins DESC;

-- Creates a view of all the players
-- and the amount of matches they have played.
CREATE VIEW MatchNumber as
	SELECT Players.id as player_id,
		   count(*) as matches
	FROM Players, Matches
	WHERE Players.id = Matches.winner 
		  OR Players.id = Matches.loser
	GROUP BY Players.id;
