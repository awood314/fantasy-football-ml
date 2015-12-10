#!/usr/bin/python3.4
# Generates files with feature featuretors for a specific position
import operator
from pymongo import MongoClient

def generate_qb_features(player, db):
    # Player collection
    playerClt = db['players']

    # returns an array of strings to write as feature vectors
    features = []

    # Compute statistics at the time of each game on a cumulative/rolling basis
    games = sorted(player['games'], key=operator.itemgetter('year','week'))
    for i in range(0,len(games)):
        if int(games[i]['snapcount']) < 15:  # only consider QBs playing a significant amount
            continue
        feature = get_feature_vectors_for_game(games, i)

        # Label: fantasy score
        score = get_fantasy_score(games[i])
        feature += format_float2str(score)
        features.append(feature)
    return features


# Get the feature vector corresponding to a single game
def get_feature_vectors_for_game(games, game_index):
    feature_vector = ""
    tot_pass_yards = 0
    tot_pass_attempts = 0
    tot_pass_completions = 0
    tot_pass_tds = 0
    tot_pass_interceptions = 0
    tot_rush_yards = 0
    tot_rush_attempts = 0
    tot_rush_tds = 0
    tot_fumbles = 0
    tot_fumbles_lost = 0

    # select the index of the game 6 games before the game at index i
    start_game = game_index-6 if game_index-6 > 0 else 0
    num_games_averaging_over = 0

    # Find averages of player's game stats over previous 6 games (if 6 exist)
    for i in range(start_game, game_index):
        game = games[i]
        if int(game['snapcount']) < 15:
            continue

        num_games_averaging_over += 1
        tot_pass_yards += game['pass_yards']
        tot_pass_attempts += game['pass_attempted']
        tot_pass_completions += game['pass_completed']
        tot_pass_tds += game['pass_touchdowns']
        tot_pass_interceptions += game['pass_interceptions']
        tot_rush_yards += game['rush_yards']
        tot_rush_attempts += game['rush_attempted']
        tot_rush_tds += game['rush_touchdowns']
        tot_fumbles += game['fumbles']
        tot_fumbles_lost += game['fumbles_lost']

    if num_games_averaging_over == 0 or tot_pass_attempts == 0:  # Avoiding divide by 0 errors
        num_games_averaging_over = 1
        tot_pass_attempts = 1
    feature_vector += format_float2str(tot_pass_completions/tot_pass_attempts) + " "
    feature_vector += format_float2str(tot_pass_yards/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_pass_tds/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_pass_interceptions/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_rush_yards/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_rush_attempts/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_rush_tds/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_fumbles/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_fumbles_lost/num_games_averaging_over) + " "
    return feature_vector


# Function to round a float to 2 decimal places, and return it as a string
def format_float2str(f):
    return "{0:.2f}".format(float(str(f)))


# Computes the fantasy score for a QB given their game stats
def get_fantasy_score(game):
    return game['pass_yards']/25 + 4*game['pass_touchdowns'] + (-2)*game['pass_interceptions'] + game['rush_yards']/10 + 6*game['rush_touchdowns'] + (-2)*game['fumbles_lost']

if __name__ == "__main__":
    # Output file(s)
    qb_file = open('qb.txt', 'w+')

    # Mongo connection
    conn = MongoClient()
    db = conn['football']
    playerClt = db['players']

    for player in playerClt.find({"position":"QB"}):
        features = generate_qb_features(player, db)
        for feature in features:
            qb_file.write(feature + "\n")
                

