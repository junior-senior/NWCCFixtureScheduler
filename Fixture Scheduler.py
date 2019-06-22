from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime


# Club classes
class Club:
    def __init__(self, club):
        self.club = club
        self.club_teams = []
        self.ground_in_use = []

    def add_team(self, team):
        self.club_teams.append(team)


class Team:
    def __init__(self, team, division):
        self.team = team
        self.division = division


class Fixture:
    def __init__(self, date, home_team, away_team):
        self.date = date
        self.home_team = home_team
        self.away_team = away_team


class FixtureList:
    def __init__(self):
        self.fixture_list = [[[]]]

# Websites to get teams from
division1_html = urlopen('http://www.nwcl.play-cricket.com/website/websites/view_division?id=83670')
division2_html = urlopen('http://www.nwcl.play-cricket.com/website/websites/view_division?id=83671')
division3_html = urlopen('http://www.nwcl.play-cricket.com/website/websites/view_division?id=83913')
division4_html = urlopen('http://www.nwcl.play-cricket.com/website/websites/view_division?id=83914')

division_site_list = []
division_site_list.append(division1_html)
division_site_list.append(division2_html)
division_site_list.append(division3_html)
division_site_list.append(division4_html)

club_list = []

for site in division_site_list:
    # Parse websites
    bs = BeautifulSoup(site.read(), 'html.parser')

    division = bs.find('div', {'class': 'col-md-6 col-sm-12 hidden-xs'}).text
    division_text_split = division.split(' ')
    if division_text_split[1] == 'One':
        division = 1
    elif division_text_split[1] == 'Two':
        division = 2
    elif division_text_split[1] == 'Three':
        division = 3
    elif division_text_split[1] == 'Four':
        division = 4

    table_body = bs.find('table', {'class': 'table table-bordered table-striped table-condensed league_table'})
    team_table = bs.findAll('a')
    teams_from_table = []
    team_pattern = r"XI$"
    team_and_division_split = []

    for entry in team_table:
        if re.search(team_pattern, entry.text):
            teams_from_table.append(entry.text)

    for team in teams_from_table:
        team_string_split = team.split(' - ')
        team_and_division_split.append(team_string_split)

    # Make new club objects
    for team in team_and_division_split:
        club_found_in_list = False
        this_club = team[0]
        this_club_team = team[1]
        team_division = division

        for clubs in club_list:
            if clubs.club == this_club:
                club_found_in_list = True
                new_team = Team(this_club_team, division)
                clubs.add_team(new_team)
                break
        if not club_found_in_list:
            new_club = Club(this_club)
            new_team = Team(this_club_team, division)
            new_club.add_team(new_team)
            club_list.append(new_club)
            club_found_in_list = False

# Now with the clubs and teams sorted, time to start on the fixtures
# I need to get a list of every Saturday from the end of April to the 1st weekend of September and store them in a list
# Create a 3D list, get the length of the list and make the 1st element of a 3D array that length
# The 2nd element will be the division
# The 3rd element will be the fixtures
# Need a list of the teams in each division
# Calculate the number of games in a season
# Find out number of off weeks
#
