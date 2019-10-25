from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime
import random
import numpy as np
import copy
from competitions.scheduler import ScheduleGenerationFailed
from competitions.scheduler.roundrobin import DoubleRoundRobinScheduler



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
        self.matches = []


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

match_days = [dstart + datetime.timedelta(days=x) for x in range((dend-dstart).days + 1)
        if (dstart + datetime.timedelta(days=x)).weekday() == 5]

# Store in list in nice format
for day in match_days:
    day_formatted = day.strftime("%A %d %B %Y")
    match_days[match_days.index(day)] = day_formatted


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
division_fixture_list = []

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

this_week_fixtures = []
for divisions in division_list:
    print("Division", division_list.index(divisions) + 1)
    division_team_list = copy.copy(divisions)

    fixtures = DoubleRoundRobinScheduler(division_team_list).generate_matches()
    rounds = DoubleRoundRobinScheduler(division_team_list).generate_round(fixtures)
    schedule = DoubleRoundRobinScheduler(division_team_list).generate_schedule()
    fixture_division = division_list.index(divisions) + 1

    f = open('Fixtures for Division {division}.txt'.format(division=fixture_division), 'w')

    for game_week in schedule:
        match_day = match_days[schedule.index(game_week)]
        f.write("Date: " + str(match_day) + "\n")
        for teams in game_week:
            home_team = teams[0]
            away_team = teams[1]
            if home_team is None:
                home_team = "None"
            if away_team is None:
                away_team = 'None'
            f.write(home_team + " V " + away_team + "\n")
        f.write("\n")

    f.close()
