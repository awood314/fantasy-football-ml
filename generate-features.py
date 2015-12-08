#!/usr/bin/python3.4
# Generates files with feature vectors for a specific position
import sys
import operator
from pymongo import MongoClient

def generate_qb_features(player, db):
    # returns an array of strings to write as feature vectors
    features = []

    # Compute statistics at the time of each game on a cumulative/rolling basis
    game_count = 0
    for game in sorted(player['games'], key=operator.itemgetter('year','week')):
        vec = ""
        vec += str(game_count) + " "

        # average passing yards
        avg_pyds = game['pyds'] if game_count == 0 else (avg_pyds + game['pyds']) / 2
        vec += str(avg_pyds) + " "

        # compute fantasy score label
        # TODO - help me lol
        score = int(game['pyds']/25) + game['ptd']*4 - game['pint']*2 + int(game['rshyds']/10) + game['rtd']*6 
        vec += str(score)
        
        features.append(vec)
        game_count += 1        

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
            print(player['name'])
            features = generate_qb_features(player, db)
            for feature in features:
                qb_file.write(feature + "\n")
                

