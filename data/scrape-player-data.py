#!/usr/bin/python3.4
# Scrapes NFL player data from pro-football-reference.com for all games in a specified year
import sys
import requests
from lxml import html
from pymongo import MongoClient

def scrape_boxscore(boxscore_url, week_num):
    # Mongodb connection
    conn = MongoClient()
    db = conn['football']
    playersClt = db['players']

    # Game Data
    page = requests.get(boxscore_url)
    tree = html.fromstring(page.content)
    teams = tree.xpath('//table[@id="linescore"]//a/text()')
    game_data = {
        "boxscore_url" : boxscore_url,
        "week"         : parse_week_num(week_num),
        "year"         : int(boxscore_url.split('boxscores/')[1][0:4]),
        "away_team"    : teams[0],
        "home_team"    : teams[1]
        }

    # Player data
    for i in range(0,2):
        snapcount_row = tree.xpath('//div[div/h2/text()="' + teams[i].split(" ")[-1] + ' Snap Counts"]/div/table/tbody/tr')
        for row in snapcount_row:
            cols = row.xpath('td')
            name = cols[0].xpath('a/text()')
	    # Apparently there is a guy with no name
            if not name:
                continue
            else:
                name = name[0]
            position = cols[1].text
            if position == 'G' or position == 'T' or position == 'C' or position == 'LT' or position == 'RT' or position == 'LG' or position == 'RG':
                position = 'OL'
            off_snapcount = cols[2].text
            if int(off_snapcount) > 0:
                player_stats = scrape_player_stats(name, tree)
                player_stats.update(game_data)
                player_stats.update({"snapcount": off_snapcount})
                playersClt.update({"name": name, "position": position, "team": teams[i]}, {'$push': {'games': player_stats}}, True)


def scrape_player_stats(name, tree):
    # Offensive stats
    off_stats_row = tree.xpath('//table[@id="skill_stats"]//tr[td/a/text()="' + name + '"]/td')
    off_stats = [0] * 17
    for i in range(2,len(off_stats_row)):
        if off_stats_row[i].text:
            off_stats[i - 2] = int(off_stats_row[i].text)

    # In starting lineup or not
    starting_lineup_row = tree.xpath('//div[@id="div_"]/*/*/*/a[text()="' + name + '"]')

    return \
        {
            "starting": 0 if not starting_lineup_row else 1,
            "pass_completed":       off_stats[0],
            "pass_attempted":       off_stats[1],
            "pass_yards":           off_stats[2],
            "pass_touchdowns":      off_stats[3],
            "pass_interceptions":   off_stats[4],
            "pass_long":            off_stats[5],
            "rush_attempted":       off_stats[6],
            "rush_yards":           off_stats[7],
            "rush_touchdowns":      off_stats[8],
            "rush_long":            off_stats[9],
            "rec_targets":          off_stats[10],
            "rec_receptions":       off_stats[11],
            "rec_yards":            off_stats[12],
            "rec_touchdowns":       off_stats[13],
            "rec_long":             off_stats[14],
            "fumbles":              off_stats[15],
            "fumbles_lost":         off_stats[16]
        }


def parse_week_num(week_num):
    if not week_num: # If None type
        return -1
    elif is_str_num(week_num):
        return int(week_num)
    elif "Wild" in week_num:
        return 18
    elif "Division" in week_num:
        return 19
    elif "Conf" in week_num:
        return 20
    elif "Super" in week_num:
        return 21
    else:
        raise ValueError("num " + week_num + " does not match any category")


def is_str_num(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: scrape-player-data.py <year>")
    
    # Get the boxscore Urls for specified year
    year = sys.argv[1]
    site = 'http://www.pro-football-reference.com'
    page = requests.get(site + '/years/' + year + '/games.htm')
    tree = html.fromstring(page.content)
    boxscore_urls = tree.xpath('//a[text()="boxscore"]/@href')
    week_nums = tree.xpath('//tr[td/a[text()="boxscore"]/@href]/td[1]/text()')

    # Scrape data for each game
    for boxscore_url, week_num in zip(boxscore_urls,week_nums):
        print("Scraping boxscore: " + site + boxscore_url)
        scrape_boxscore(site + boxscore_url, week_num)


