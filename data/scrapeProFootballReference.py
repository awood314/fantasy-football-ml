#/usr/bin/python27
# Crawls NFL player data for all games in a specified year
import sys
import requests
from lxml import html
from pymongo import MongoClient

def scrape_boxscore(boxscore_url, db):
    # Mongo collections
    players = db['players']

    # Game data
    game_id = boxscore_url.split('boxscores/')[1]
        
    # Get the list of player names for each team
    page = requests.get(boxscore_url)
    tree = html.fromstring(page.content)
    teams = tree.xpath('//a[@href="#top"]/text()')[0].split(' @ ')
    player_names = [] # away, home
    player_names.append(tree.xpath('//h2[text()="' + teams[0] + ' Snap Counts"]/../..//td[@align="left"]/a/text()'))
    player_names.append(tree.xpath('//h2[text()="' + teams[1] + ' Snap Counts"]/../..//td[@align="left"]/a/text()'))
    
    # Scrape player data for the game and add their game data to their collection
    for i in range(0,2): 
        for name in player_names[i]:
            player_data = scrape_player(name, teams[i], tree)
            players.update({'name':name, 'game':game_id}, player_data, upsert=True)

def scrape_player(name, team, tree):
    snapcount = tree.xpath('//div[div/h2/text()="' + team + ' Snap Counts"]//tr[td/a/text()="' + name + '"]/td')
    pos = snapcount[1].text
    return {'name': name, 
            'pos' : pos }
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: scrape.py <year>"
    
    # Mongodb connection
    conn = MongoClient()
    db = conn['football']

    # Get the boxscore Urls for specified year
    year = sys.argv[1]
    site = 'http://www.pro-football-reference.com'
    page = requests.get(site + '/years/' + year + '/games.htm')
    tree = html.fromstring(page.content)
    boxscore_urls = tree.xpath('//a[text()="boxscore"]/@href')

    # Scrape data for each game
    for boxscore_url in boxscore_urls:
        scrape_boxscore(site + boxscore_url, db)

