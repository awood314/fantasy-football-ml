#!/usr/bin/python3.4
# Generates files with feature featuretors for a specific position
import sys
import operator
from pymongo import MongoClient

def generate_features(player, db, year):
    teamClt = db['teams']
    espnClt = db['espnProjections']
    # returns an array of strings to write as feature vectors
    features = []

    # Compute statistics at the time of each game on a cumulative/rolling basis
    games = sorted(player['games'], key=operator.itemgetter('year', 'week'))

    position = player['position']
    team = player['team']
    team_doc = teamClt.find_one({"team": team})
    team_games = sorted(team_doc['games'], key=operator.itemgetter('year', 'week'))

    # Gather this players useful games
    useful_games = []
    for i in range(0,len(games)):
        if int(games[i]['snapcount']) >= 15 and games[i]['year'] <= year:  # only consider players playing a significant amount
            useful_games.append(games[i])

    # Create feature vector for each useful game
    if len(useful_games) > 1:
        for i in range(1, len(useful_games)):
            game = useful_games[i]

            # Player features
            feature = get_features_player_stats(useful_games, i, position)

            # Team features
            team_game_index = next(team_games.index(g) for g in team_games
                               if g['week'] == game['week'] and g['year'] == game['year'])
            feature += get_features_team_stats(team_games, team_game_index, 6)
            # feature += get_features_team_stats(team_games, team_game_index, 16)

            # Opponent features
            opp = game['away_team'] if game['home_team'] == player['team'] else game['home_team']
            opp_games = sorted(teamClt.find_one({"team":opp})['games'], key=operator.itemgetter('year','week'))
            opp_game_index = next(opp_games.index(g) for g in opp_games 
                                if g['week'] == game['week'] and g['year'] == game['year'])
            feature += get_features_opp_stats(opp_games, opp_game_index, 6)
            # feature += get_features_opp_stats(opp_games, opp_game_index, 16)

            # Label: fantasy score
            score = get_fantasy_score(game)
            feature += format_float2str(score) + ' '

            # Add on ESPNprojection
            espnProjection = espnClt.find_one({"name":player['name'], "week":game['week']})
            if espnProjection and espnProjection['projectedPoints'] != '--':
                feature += str(espnProjection['projectedPoints'])
            else:
                feature += '-99'
            features.append(feature)
    return features


def get_features_team_stats(games, game_index, num_games_avg):
    feature_vector = ""
    team_total_yards = 0
    team_pass_yards = 0
    team_rush_yards = 0
    team_points = 0
    team_turnovers = 0

    # select the index of the game num_games_avg games before the game at index i, or 0 if negative
    start_game = game_index-num_games_avg if game_index-num_games_avg > 0 else 0
    num_games_averaging_over = 0

    # Find averages of team's game stats over previous num_games_avg games
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

# Get the feature vector corresponding to an opponent team's defensive stats
def get_features_opp_stats(games, game_index, num_games_avg):
    feature_vector = ""
    points_allowed = 0
    total_yards_allowed = 0
    pass_yards_allowed = 0
    rush_yards_allowed = 0
    turnovers_forced = 0

    # select the index of the game num_games_to_average_over games before the game at index i, or 0 if negative
    start_game = game_index-num_games_avg if game_index-num_games_avg > 0 else 0
    num_games_averaging_over = 0

    # Find averages of team's game stats over previous num_games_avg games
    for i in range(start_game, game_index):
        game = games[i]

        num_games_averaging_over += 1
        points_allowed += game['opponent_points']
        total_yards_allowed += game['total_yards_allowed']
        pass_yards_allowed += game['pass_yards_allowed']
        rush_yards_allowed += game['rush_yards_allowed']
        turnovers_forced += game['turnovers_forced']

    if num_games_averaging_over == 0:  # Avoiding divide by 0 errors
        num_games_averaging_over = 1

    feature_vector += format_float2str(points_allowed/num_games_averaging_over) + " "
    feature_vector += format_float2str(total_yards_allowed/num_games_averaging_over) + " "
    feature_vector += format_float2str(pass_yards_allowed/num_games_averaging_over) + " "
    feature_vector += format_float2str(rush_yards_allowed/num_games_averaging_over) + " "
    feature_vector += format_float2str(turnovers_forced/num_games_averaging_over) + " "

    return feature_vector


# Get player stats as features based on position
def get_features_player_stats(games, game_index, position):
    feature_vector = ""
    if position == 'RB':
        feature_vector += add_features_player_rushing_stats(games, game_index, 6)
        feature_vector += add_features_player_rushing_stats(games, game_index, 16)
        feature_vector += add_features_player_receiving_stats(games, game_index, 6)
    elif position == 'QB':
        feature_vector += add_features_player_rushing_stats(games, game_index, 6)
        feature_vector += add_features_player_passing_stats(games, game_index, 6)
        feature_vector += add_features_player_passing_stats(games, game_index, 16)
    elif position == 'WR':
        feature_vector += add_features_player_rushing_stats(games, game_index, 6)
        feature_vector += add_features_player_receiving_stats(games, game_index, 6)
        feature_vector += add_features_player_receiving_stats(games, game_index, 16)
    return feature_vector



# Get the features for a player's passing stats
def add_features_player_passing_stats(games, game_index, num_games_avg):
    feature_vector = ""
    tot_pass_yards = 0
    tot_pass_attempts = 0
    tot_pass_completions = 0
    tot_pass_tds = 0
    tot_pass_interceptions = 0

    # select the index of the game num_games_avg games before the game at index i
    start_game = game_index-num_games_avg if game_index-num_games_avg > 0 else 0
    num_games_averaging_over = 0

    # Find averages of player's game stats over previous num_games_avg games
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

    if num_games_averaging_over == 0 or tot_pass_attempts == 0:  # Avoiding divide by 0 errors
        num_games_averaging_over = 1
        tot_pass_attempts = 1
    feature_vector += format_float2str(games[game_index]['starting']) + " "
    feature_vector += format_float2str(tot_pass_completions/tot_pass_attempts) + " "
    feature_vector += format_float2str(tot_pass_yards/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_pass_tds/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_pass_interceptions/num_games_averaging_over) + " "
    return feature_vector


# Get the features for a player's rushing stats
def add_features_player_rushing_stats(games, game_index, num_games_avg):
    feature_vector = ""
    tot_rush_yards = 0
    tot_rush_attempts = 0
    tot_rush_tds = 0
    tot_fumbles = 0
    tot_fumbles_lost = 0

    # select the index of the game 6 games before the game at index i
    start_game = game_index-num_games_avg if game_index-num_games_avg > 0 else 0
    num_games_averaging_over = 0

    # Find averages of player's game stats over previous num_games_avg games
    for i in range(start_game, game_index):
        game = games[i]
        if int(game['snapcount']) < 15:
            continue

        num_games_averaging_over += 1
        tot_rush_yards += game['rush_yards']
        tot_rush_attempts += game['rush_attempted']
        tot_rush_tds += game['rush_touchdowns']
        tot_fumbles += game['fumbles']
        tot_fumbles_lost += game['fumbles_lost']

    if num_games_averaging_over == 0:  # Avoiding divide by 0 errors
        num_games_averaging_over = 1
    feature_vector += format_float2str(games[game_index]['starting']) + " "
    feature_vector += format_float2str(tot_rush_yards/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_rush_attempts/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_rush_tds/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_fumbles/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_fumbles_lost/num_games_averaging_over) + " "
    return feature_vector


# Get the features for a player's receiving stats
def add_features_player_receiving_stats(games, game_index, num_games_avg):
    feature_vector = ""
    tot_rec_yards = 0
    tot_rec_receptions = 0
    tot_rec_targets = 0
    tot_rec_tds = 0

    # select the index of the game num_games_avg games before the game at index i
    start_game = game_index-num_games_avg if game_index-num_games_avg > 0 else 0
    num_games_averaging_over = 0

    # Find averages of player's game stats over previous num_games_avg games
    for i in range(start_game, game_index):
        game = games[i]
        if int(game['snapcount']) < 15:
            continue

        num_games_averaging_over += 1
        tot_rec_yards += game['rec_yards']
        tot_rec_receptions += game['rec_receptions']
        tot_rec_targets += game['rec_targets']
        tot_rec_tds += game['rec_touchdowns']

    if num_games_averaging_over == 0:  # Avoiding divide by 0 errors
        num_games_averaging_over = 1
    feature_vector += format_float2str(tot_rec_yards/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_rec_receptions/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_rec_targets/num_games_averaging_over) + " "
    feature_vector += format_float2str(tot_rec_tds/num_games_averaging_over) + " "
    return feature_vector


# Function to round a float to 2 decimal places, and return it as a string
def format_float2str(f):
    return "{0:.2f}".format(float(str(f)))


# Computes the fantasy score for a QB given their game stats
def get_fantasy_score(game):
    return game['pass_yards']/25 + 4*game['pass_touchdowns'] + (-2)*game['pass_interceptions'] \
           + game['rush_yards']/10 + 6*game['rush_touchdowns'] + (-2)*game['fumbles_lost'] \
           + game['rec_yards']/10 + 6*game['rec_touchdowns']

if __name__ == "__main__":
    # Mongo connection
    conn = MongoClient()
    db = conn['football']
    playerClt = db['players']

    qb_file = open('qbtrain.txt', 'w')
    for player in playerClt.find({"position":"QB"}):
        features = generate_features(player, db, 2013)
        for feature in features:
            qb_file.write(feature + "\n")
    qb_file.close()

    # RB train data
    rb_file = open('rbtrain.txt', 'w')
    for player in playerClt.find({"position":"RB"}):
        features = generate_features(player, db, 2013)
        for feature in features:
            rb_file.write(feature + "\n")
    rb_file.close()

    # WR train data
    wr_file = open('wrtrain.txt', 'w')
    for player in playerClt.find({"position":"WR"}):
        features = generate_features(player, db, 2013)
        for feature in features:
            wr_file.write(feature + "\n")
    wr_file.close()
