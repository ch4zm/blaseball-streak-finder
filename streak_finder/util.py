import json
import os
import blaseball_core_game_data as gd


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = os.path.abspath(os.path.join(root_path, 'data'))

SHORT2LONG_JSON = os.path.join(data_path, "short2long.json")

DALE_SAFE = "Dale" # for command line
DALE_UTF8 = "Dal\u00e9" # for display

FULL_DALE_SAFE = "Miami Dale" # for command line
FULL_DALE_UTF8 = "Miami Dal\u00e9" # for display


def get_league_division_team_data():
    """
    Get a list of leagues, divisions, and teams.
    This is for use in creating CLI flag values,
    so we replace Dal\u00e9 with Dale.
    """
    td = json.loads(gd.get_teams_data())
    leagues = sorted(list(td['leagues'].keys()))
    divisions = sorted(list(td['divisions'].keys()))
    teams = []
    for league in leagues:
        teams += td['leagues'][league]
    teams = sorted(list(teams))
    teams = [sanitize_dale(s) for s in teams]
    return (leagues, divisions, teams)


def league_to_teams(league):
    """
    For a given league, return a list of all teams in that league.
    We replace Dal\u00e9 with Dale (see above).
    """
    td = json.loads(gd.get_teams_data())
    teams = []
    teams += td['leagues'][league]
    teams = [sanitize_dale(s) for s in teams]
    return teams


def division_to_teams(division):
    """
    For a given division, return a list of all teams in that league.
    We replace Dal\u00e9 with Dale (see above).
    """
    td = json.loads(gd.get_teams_data())
    teams = []
    teams += td['divisions'][division]
    teams = [sanitize_dale(s) for s in teams]
    return teams


def get_short2long():
    """Get the map of team nicknames to team full names"""
    short2long = None
    if os.path.exists(SHORT2LONG_JSON):
        with open(SHORT2LONG_JSON, 'r') as f:
            short2long = json.load(f)
    else:
        raise FileNotFoundError("Missing team nickname to full name data file: %s"%(SHORT2LONG_JSON))
    return short2long



def desanitize_dale(s):
    """Utility function to change sanitized Dale back to unicode"""
    if s == DALE_SAFE:
        return DALE_UTF8
    elif s == FULL_DALE_SAFE:
        return FULL_DALE_UTF8
    else:
        return s


def sanitize_dale(s):
    """Utility function to make CLI flag value easier to set"""
    if s == DALE_UTF8:
        return DALE_SAFE
    elif s== FULL_DALE_UTF8:
        return FULL_DALE_SAFE
    else:
        return s
