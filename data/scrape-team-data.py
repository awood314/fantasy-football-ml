#!/usr/bin/python3.4
# Scrapes NFL game data from pro-football-reference.com for every active franchise
import sys
import requests
from lxml import html
from pymongo import MongoClient

def scrape_team_stats(team_year_url, year):
    # Mongodb connection
    conn = MongoClient()
    db = conn['football']
    teamClt = db['teams']

    # Team data for each game
    page = requests.get(team_year_url)
    tree = html.fromstring(page.content)
    team_name = tree.xpath('//h1/text()')[0].split(' ', 1)[1]
    
    game_logs = tree.xpath('//table[@id="team_gamelogs"]//tr[td[4]/a/@href]')
    for game in game_logs:
        game_stats = scrape_game_stats(game, team_name, year)
        teamClt.update({"team": team_name}, {'$push': {'games': game_stats}}, True)


def scrape_game_stats(game_row, team_name, year):
    cols = game_row.xpath('td')
    week = parse_week_num(cols[0].text)

    if cols[4].text: # Check if game has been played or not yet
        game_stats = \
            {
                "week": week,
                "year": year,
                "points": int(cols[9].text),
                "opponent_points": int(cols[10].text),
                "total_yards": int(cols[12].text),
                "pass_yards": int(cols[13].text),
                "rush_yards": int(cols[14].text),
                "turnovers": 0 if not cols[15].text else int(cols[15].text),
                "total_yards_allowed": int(cols[17].text),
                "pass_yards_allowed": int(cols[18].text),
                "rush_yards_allowed": int(cols[19].text),
                "turnovers_forced": 0 if not cols[20].text else int(cols[20].text)
            }
    return game_stats


def parse_week_num(week_num):
    if not week_num: # If None type
        return -1
    elif is_str_num(week_num): # If a number
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
        print("usage: scrape-team-data.py <earliest year>")
    
    # Get the urls for each team
    site = 'http://www.pro-football-reference.com'
    page = requests.get(site + '/teams/')
    tree = html.fromstring(page.content)
    team_urls = tree.xpath('//table[@id="teams_active"]//a[contains(@href,"/teams/")]/@href')

    min_year = int(sys.argv[1])
    for team_url in team_urls:
        for year in range(min_year, 2015):
            print("scraping team stats: " + site + team_url + str(year) + '.htm')
            scrape_team_stats(site + team_url + str(year) + '.htm', year)
