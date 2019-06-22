from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


# Club classes
class Club:
    club_teams = []

    def __init__(self, club):
        self.club = club

    class Team:
        def __init__(self, team, division):
            self.team = team
            self.division = division


class Fixture:
    def __init__(self, date, home_team, away_team):
        self.date = date
        self.home_team = home_team
        self.away_team = away_team


# Websites to get teams from
division1_html = urlopen('http://www.nwcl.play-cricket.com/website/websites/view_division?id=83670')
division2_html = urlopen('http://www.nwcl.play-cricket.com/website/websites/view_division?id=83671')
division3_html = urlopen('http://www.nwcl.play-cricket.com/website/websites/view_division?id=83913')
division4_html = urlopen('http://www.nwcl.play-cricket.com/website/websites/view_division?id=83914')

# Parse websites
bs = BeautifulSoup(division1_html.read(), 'html.parser')

table_body = bs.find('table', {'class': 'table table-bordered table-striped table-condensed league_table'})
team_table = bs.findAll('a')
teams_from_table = []
team_pattern = r"XI$"
team_and_division_split = []
club_list = []

for entry in team_table:
    if re.search(team_pattern, entry.text):
        teams_from_table.append(entry.text)

for team in teams_from_table:
    team_string_split = team.split(' - ')
    team_and_division_split.append(team_string_split)

# Make new club objects
for team in team_and_division_split:
    club = team[0]
    new_club = Club(club)
    club_list.append(new_club)

for club in club_list:
    team = club.Team()
# Make a list of clubs and their teams
# Each team in teams_from_table needs to check if club exists (should only be for 2nd XI)
# Check club list if club already exists
# If no, add new club and team
# If yes, add new team
