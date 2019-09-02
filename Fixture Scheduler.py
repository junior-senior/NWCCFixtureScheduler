from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime
import random
import numpy as np
import copy


# Club classes
class Club:
    def __init__(self, club, number_of_match_days):
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
    def __init__(self, match_day, division, fixture_count):
        self.fixture_list = []


# Get days teams can play on
dstart = datetime.date(2020, 4, 11)
dend = datetime.date(2020, 9, 10)

days = [dstart + datetime.timedelta(days=x) for x in range((dend-dstart).days + 1)
        if (dstart + datetime.timedelta(days=x)).weekday() == 5]

# Store in list in nice format
for day in days:
    day_formatted = day.strftime("%A %d %B %Y")
    days[days.index(day)] = day_formatted


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
            new_club = Club(this_club, len(days))
            new_team = Team(this_club_team, division)
            new_club.add_team(new_team)
            club_list.append(new_club)
            club_found_in_list = False


# Get lists for team divisions
division1_team_list = []
division2_team_list = []
division3_team_list = []
division4_team_list = []

for clubs in club_list:
    for teams in clubs.club_teams:
        if teams.division == 1:
            division1_team_list.append("{club} {team}".format(club=clubs.club, team=teams.team))
        if teams.division == 2:
            division2_team_list.append("{club} {team}".format(club=clubs.club, team=teams.team))
        if teams.division == 3:
            division3_team_list.append("{club} {team}".format(club=clubs.club, team=teams.team))
        if teams.division == 4:
            division4_team_list.append("{club} {team}".format(club=clubs.club, team=teams.team))

division_list = []

division_list.append(division1_team_list)
division_list.append(division2_team_list)
division_list.append(division3_team_list)
division_list.append(division4_team_list)

# for divisions in range(0, len(division_list)):
#     division_teams_list = division_list[divisions]
#     fixture_list.fixture_list = [[days], [divisions], [len(division_teams_list)]]

home_team = ''
away_team = ''
match_day_fixtures = []
team_list = list(division1_team_list)


def pick_teams(team_list, match_day, fixture_list):
    home_team = random.choice(team_list)
    away_team = random.choice(team_list)
    home_team, away_team = check_fixture(home_team, away_team, team_list, fixture_list)
    match_day_index = days.index(match_day)
    for clubs in club_list:
        if clubs.club == home_team.strip(' 1st XI'):
            # print(clubs.club, match_day_index)
            clubs.ground_in_use.append(True)
            break
        if clubs.club == away_team.strip(' 1st XI'):
            # print(clubs.club, match_day_index)
            clubs.ground_in_use.append(False)
            break
    try:
        team_list.remove(home_team)
        team_list.remove(away_team)
        return home_team, away_team
    except ValueError:
        pass


def check_fixture(home_team, away_team, team_list, fixture_list):
    fixture = "{home} v {away}".format(home=home_team, away=away_team)
    if home_team == away_team:
        team_list.remove(home_team)
        try:
            away_team = random.choice(team_list)
            team_list.append(home_team)
            check_fixture(home_team, away_team, team_list, fixture_list)
        except IndexError:
            pass
    # for fixtures in fixture_list:
    #     if fixture in fixture_list:
    #         away_team = random.choice(team_list)
    #         check_fixture(home_team, away_team, team_list, fixture_list)
    return home_team, away_team

fixture_count = 0

this_week_fixtures = []
for divisions in division_list:
    fixture_list = FixtureList(len(days), division_list.index(divisions), int(len(team_list) / 2))
    for match_day in days:
        team_list = copy.copy(divisions)
        while len(team_list) > 0:
            try:
                home_team, away_team = pick_teams(team_list, match_day, fixture_list.fixture_list)
                fixture = "{home} v {away}".format(home=home_team, away=away_team)
                this_week_fixtures.append(fixture)
            except TypeError:
                pass
        fixture_list.fixture_list.append(this_week_fixtures)
        this_week_fixtures = []
    fixture_division = division_list.index(divisions) + 1

    f = open('Fixtures for Division {division}.txt'.format(division=fixture_division), 'w')
    for lines in fixture_list.fixture_list:
        f.write(str(lines) + "\n")
    f.close()
# Randomly pick home and away team from the division team list,
# Check match hasn't happened before (exact string match in fixture list)
# If yes, reverse fixture
# Check match hasn't happened before (exact string match in fixture list)
# If it has, check home ground isn't in use
# pick new away team
# Repeat above
# If hasn't
# Check home ground is available
# If it is
# add to teams picked list, append ground in use to True
# Pick another team, add to team picked list
# add to Fixture List
# repeat until len picked teams = len division team list
# Reset Picked Teams
# Do next match day
# Randomly pick as team from the division team list, add to team picked list, check ground in use for that day
# Pick another team, add to team picked list, if ground is in use, check this teams ground, if both in use
# pick new home team
# add to Fixture List
# repeat until len picked teams = len division team list
