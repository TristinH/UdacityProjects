#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


# Connect to the PostgreSQL database.  Returns a database connection.
def connect():
    return psycopg2.connect("dbname=tournament")


# Remove all the match records from the database.
def deleteMatches():  
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM Matches")
    db.commit()
    c.close()


# Remove all the player records from the database.
def deletePlayers():  
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM Players")
    db.commit()
    c.close()


# Returns the number of players currently registered.
def countPlayers():
    db = connect()
    c = db.cursor()
    c.execute("SELECT count(*) FROM Players")
    player_count = c.fetchone()
    # check if any players have been added
    if not player_count:
    	count = 0
    else:
    	count = player_count[0]
    c.close()
    return count


# Adds a player to the tournament database.
# The database assigns a unique serial id number for the player.  
# Args:
#  name: the player's full name (need not be unique).
def registerPlayer(name):
	db = connect()
	c = db.cursor()
	c.execute("INSERT INTO Players (name) VALUES (%s)", (name,))
	db.commit()
	c.close()

    
# Returns a list of the players and their win records, sorted by wins.
# This function uses views to test if there are any matches to begin
# with. If there aren't it will return a list with wins and matches
# both given a value of 0.
# Returns:
#  A list of tuples, each of which contains (id, name, wins, matches):
#   id: the player's unique id (assigned by the database)
#   name: the player's full name (as registered)
#   wins: the number of matches the player has won
#   matches: the number of matches the player has played
def playerStandings():
	# empty list to hold the players
	player_list = []

	db = connect()
	c = db.cursor()
	c.execute("SELECT * FROM Matches")
	players = c.fetchall()

	# check if there are any matches have been played
	if not players:
		c.execute("SELECT * FROM Players")
		players = c.fetchall()
		for player in players:
			# get the player's id and name
			player_id = player[0]
			name = player[1]

			# append the record to the list with 0 wins and
			# 0 matches since no matches have been played yet
			player_list.append((player_id, name, 0, 0))
	# if matches have been played get the order from PlayerOrder view
	else:
		c.execute("SELECT * FROM PlayerOrder")
		players = c.fetchall()
		for player in players:
			# get the player's id and wins
			player_id = player[0]
			wins = player[1]

			# get the player's name
			c.execute("SELECT name FROM Players WHERE id = %s" % (player_id,))
			name = c.fetchone()[0]

			# get the amount of matches the player has played
			c.execute("SELECT matches FROM MatchNumber WHERE player_id = %s"
					  % (player_id,))
			matches = c.fetchone()[0]

			# add the player to the list
			player_list.append((player_id, name, wins, matches))
	c.close()
	return player_list


# Records the outcome of a single match between two players.
# Args:
#   winner:  the id number of the player who won
#   loser:  the id number of the player who lost
def reportMatch(winner, loser):
	db = connect()
	c = db.cursor()
	c.execute("INSERT INTO Matches (winner, loser) VALUES (%s, %s)", 
			  (winner, loser))
	db.commit()
	c.close()
 
 
# Returns a list of pairs of players for the next round of a match.
# Assuming that there are an even number of players registered, each player
# appears exactly once in the pairings.  Each player is paired with another
# player with an equal or nearly-equal win record, that is, a player adjacent
# to him or her in the standings.
# Returns:
#   A list of tuples, each of which contains (id1, name1, id2, name2)
#     id1: the first player's unique id
#     name1: the first player's name
#     id2: the second player's unique id
#     name2: the second player's name
def swissPairings():
	# match opponents based on current standings
	player_list = playerStandings()
	pairings = []
	i = 1
	while i < len(player_list):
		# get the players to be paired
		player1 = player_list[i-1]
		player2 = player_list[i]

		# get the player ids and names
		id1 = player1[0]
		name1 = player1[1]

		id2 = player2[0]
		name2 = player2[1]

		# add the pairing to the list
		pairings.append((id1, name1, id2, name2))
		i += 2
	return pairings
