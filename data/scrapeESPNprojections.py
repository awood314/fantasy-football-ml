from pymongo import MongoClient
from lxml import html
import requests

__author__ = 'Garrett Johnston'

client = MongoClient()
db = client.football

baseURL = 'https://web.archive.org/web/20140905214405/http://games.espn.go.com/ffl/tools/projections?'

for weekNum in range(1, 18):
    print(weekNum)
    for positionId in range(0, 7, 2):
        url = baseURL + '&scoringPeriodId=' + str(weekNum) + '&seasonId=2014&slotCategoryId=' + str(positionId)

        page = requests.get(url)
        tree = html.fromstring(page.content)

        playerNames = tree.xpath('//td[@class="playertablePlayerName"]/a/text()')
        projections = tree.xpath(
            '//td[contains(@class,\'playertableStat\') and contains(@class,\'appliedPoints\')]/text()')
        teams = tree.xpath('//td[@class="playertablePlayerName"]/text()')

        # Clean up team name data
        for i in range(0, len(teams)):
            teams[i] = teams[i].split()[1]

        # Gather data from second page
        if positionId != 0:
            # Get second page using this url
            page = requests.get(url + '&startIndex=40')
            tree = html.fromstring(page.content)

            playerNames.extend(tree.xpath('//td[@class="playertablePlayerName"]//a/text()'))
            projections.extend(tree.xpath(
                '//td[contains(@class,\'playertableStat\') and contains(@class,\'appliedPoints\') and contains(@class,\'sortedCell\')]/text()'))
            teamsPage2 = tree.xpath('//td[@class="playertablePlayerName"]/text()')

            for i in range(0, len(teamsPage2)):
                teamsPage2[i] = teamsPage2[i].split()[1]

            teams.extend(teamsPage2)

        print(len(playerNames), playerNames)
        print(len(projections), projections)
        print(len(teams), teams)

        for playerName, team, projection in zip(playerNames, teams, projections):
            db['espnProjections'].insert_one(
                {
                    "name": playerName,
                    "team": team,
                    "week": weekNum,
                    "projectedPoints": projection
                }
            )
