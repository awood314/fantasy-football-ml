#/usr/bin/python27
# Crawls NFL player data for all games in a specified year

import sys
import requests
from lxml import html

def scrape_boxscore(boxscore_url):
    page = requests.get(boxscore_url)
    tree = html.fromstring(page.content)

    teams = tree.xpath('//a[@href="#top"]/text()')[0].split(' @ ')
    hometeam = teams[1]
    awayteam = teams[0]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: scrape.py <year>"
    
    year = sys.argv[1]
    page = requests.get('http://www.pro-football-reference.com/years/' + year + '/games.htm')
    tree = html.fromstring(page.content)
    boxscore_urls = tree.xpath('//a[text()="boxscore"]/@href')
    for boxscore_url in boxscore_urls:
        scrape_boxscore(boxscore_url)

