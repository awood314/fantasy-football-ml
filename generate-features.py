#!/usr/bin/python3.4
# Generates files with feature featuretors for a specific position
import sys
import operator
from pymongo import MongoClient

def generate_qb_features(player, db):
    # Player collection
    playerClt = db['players']

    # returns an array of strings to write as feature vectors
    features = []

    # Compute statistics at the time of each game on a cumulative/rolling basis
    games = sorted(player['games'], key=operator.itemgetter('year','week'))
    avg_pyds = games[0]['pyds']
    avg_rshyds = games[0]['rshyds']
    avg_pass_pct = games[0]['pcmp'] / games[0]['patt']
    game_count = 1
    for game in games[1:]:
        feature = ""

        # Total number of games played
        feature += str(game_count) + " "
        game_count += 1        

        # average passing yards
        avg_pyds = (avg_pyds + game['pyds']) / 2.
        feature += str(avg_pyds) + " "
        
        # average rushing yards
        avg_rshyds = (avg_rshyds + game['rshyds']) / 2.
        feature += str(avg_rshyds) + " "

        # average pass percentage
        avg_pass_pct = (avg_pass_pct + (game['pcmp'] + game['patt'])) / 2
        feature += str(avg_pass_pct) + " "

        # Label: fantasy score
        # TODO - help plz
        score = int(game['pyds']/25) + game['ptd']*4 - game['pint']*2 + int(game['rshyds']/10) + game['rtd']*6 
        feature += str(score)
        features.append(feature)
    return features


if __name__ == "__main__":
    # Output file(s)
    qb_file = open('qb.txt', 'w+')

    # Mongo connection
    conn = MongoClient()
    db = conn['football']
    playerClt = db['players']

    for player in playerClt.find():
        if player['position'] == 'QB':
            features = generate_qb_features(player, db)
            for feature in features:
                qb_file.write(feature + "\n")
                

