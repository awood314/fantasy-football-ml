#/usr/bin/python27
# Crawls NFL player data for all games in a specified year
import sys
import requests
from lxml import html
from pymongo import MongoClient

def scrape_boxscore(boxscore_url, db):
    # Mongo collections
    playersClt = db['players']

    # Get team names
    page = requests.get(boxscore_url)
    tree = html.fromstring(page.content)
    teams = tree.xpath('//a[@href="#top"]/text()')[0].split(' @ ')

    # Game data
    game_data = {
        "game_id" : boxscore_url.split('boxscores/')[1],
        "away_team": teams[0],
        "home_team": teams[1]
        }


    for i in range(0,2):
        snapcount_row = tree.xpath('//div[div/h2/text()="' + teams[i] + ' Snap Counts"]/div/table/tbody/tr')
        players = []
        for row in snapcount_row:
            cols = row.xpath('td')
            name = cols[0].xpath('a')[0].text
            position = cols[1].text
            off_snapcount = cols[2].text
            if int(off_snapcount) > 0:
                player_stats = scrape_player_stats(name, tree)
                player_stats.update(game_data)
                player_stats.update({"snapcount": off_snapcount})
                playersClt.update({"name": name, "position": position, "team": teams[i]}, {'$push': {'games': player_stats}}, True)

# Game stats & data
def scrape_player_stats(name, tree):
    off_stats_row = tree.xpath('//table[@id="skill_stats"]//tr[td/a/text()="' + name + '"]/td')
    off_stats = [0] * 17
    for i in range(2,len(off_stats_row)):
        if off_stats_row[i].text:
            off_stats[i - 2] = int(off_stats_row[i].text)

    return \
        {
            "pcmp": off_stats[0],
            "patt": off_stats[1],
            "pyds": off_stats[2],
            "ptd":  off_stats[3],
            "pint": off_stats[4],
            "plng": off_stats[5],
            "ratt": off_stats[6],
            "rshyds": off_stats[7],
            "rtd": off_stats[8],
            "rlng": off_stats[9],
            "rtgt": off_stats[10],
            "rrec": off_stats[11],
            "recyds": off_stats[12],
            "rectd": off_stats[13],
            "reclng": off_stats[14],
            "fmb": off_stats[15],
            "fmbl": off_stats[16]
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: scrape.py <year>")
    
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
        print('scraping game', boxscore_url)
        scrape_boxscore(site + boxscore_url, db)