#!/usr/bin/python3.4
# Scrapes NFL game data from pro-football-reference.com for every active franchise
import sys
import requests
from lxml import html
from pymongo import MongoClient

def scrape_team_stats(team_year_url):
    # Mongodb connection
    conn = MongoClient()
    db = conn['football']
    teamClt = db['teams']

    # Team data for each game
    page = requests.get(team_year_url)
    tree = html.fromstring(page.content)
    name = tree.xpath('//h1/text()')[0].split(' ',1)[1]
    
    game_logs = tree.xpath('//table[@id="team_gamelogs"]//tr')
    # TODO - collect offensive and deffensive stats for each game

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: scrape-team-data.py <earliest year>")
    
    # Get the urls for each team
    site = 'http://www.pro-football-reference.com'
    page = requests.get(site + '/teams/')
    tree = html.fromstring(page.content)
    team_urls = tree.xpath('//table//a[contains(@href,"/teams/")]/@href')

    min_year = int(sys.argv[1])
    for team_url in team_urls:
        for year in range(min_year, 2016):
            scrape_team_stats(site + team_url + str(year) + '.htm')
