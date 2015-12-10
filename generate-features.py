#!/usr/bin/python3.4
# Generates files with feature featuretors for a specific position
import operator
from pymongo import MongoClient

def generate_qb_features(player, db):
    teamClt = db['teams']
    # returns an array of strings to write as feature vectors
    features = []

    # Compute statistics at the time of each game on a cumulative/rolling basis
    games = sorted(player['games'], key=operator.itemgetter('year', 'week'))
    team = player['team']
    team_doc = teamClt.find_one({"team": team})
    team_games = sorted(team_doc['games'], key=operator.itemgetter('year', 'week'))

    # Gather this players useful games
    useful_games = []
    for i in range(0,len(games)):
        if int(games[i]['snapcount']) < 15:  # only consider QBs playing a significant amount
            continue
        else:
            useful_games.append(games[i])

    # Create feature vector for each useful game
    if len(useful_games) > 1:
        for i in range(1, len(useful_games)):
            feature = get_features_player_stats(useful_games, i)
            team_game_index = next(team_games.index(g) for g in team_games
                               if g['week'] == useful_games[i]['week'] and g['year'] == useful_games[i]['year'])
            feature += get_features_team_stats(team_games, team_game_index)
            # Label: fantasy score
            score = get_fantasy_score(useful_games[i])

            feature += format_float2str(score)
            features.append(feature)
    return features


def get_features_team_stats(games, game_index):
    feature_vector = ""
    team_total_yards = 0
    team_pass_yards = 0
    team_rush_yards = 0
    team_points = 0
    team_turnovers = 0

    # select the index of the game 6 games before the game at index i, or 0 if negative
    start_game = game_index-6 if game_index-6 > 0 else 0
    num_games_averaging_over = 0

    # Find averages of team's game stats over previous 6 games (if 6 exist)
    for i in range(start_game, game_index):
        game = games[i]

        num_games_averaging_over += 1
        team_total_yards += game['total_yards']
        team_pass_yards += game['pass_yards']
        team_rush_yards += game['rush_yards']
        team_points += game['points']
        team_turnovers += game['turnovers']

    if num_games_averaging_over == 0:  # Avoiding divide by 0 errors
        num_games_averaging_over = 1

    feature_vector += format_float2str(team_total_yards/num_games_averaging_over) + " "
    feature_vector += format_float2str(team_pass_yards/num_games_averaging_over) + " "
    feature_vector += format_float2str(team_rush_yards/num_games_averaging_over) + " "
    feature_vector += format_float2str(team_points/num_games_averaging_over) + " "
    feature_vector += format_float2str(team_turnovers/num_games_averaging_over) + " "
    return feature_vector


# Get the feature vector corresponding to a single game
def get_features_player_stats(games, game_index):
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
    feature_vector += format_float2str(games[game_index]['starting']) + " "
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
                
    qb_file.close()
