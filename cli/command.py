import sys
import os
import json
import configargparse
from .view import TextView, HtmlView
from .util import sanitize_dale, desanitize_dale


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = os.path.abspath(os.path.join(root_path, 'data'))

GAMES_DATA_JSON = os.path.join(data_path, "games_data_trim.json")
TEAMS_DATA_JSON = os.path.join(data_path, "teams_data.json")


def main(sysargs = sys.argv[1:]):

    p = configargparse.ArgParser()

    # These are safe for command line usage (no accent in Dale)
    LEAGUES, DIVISIONS, ALLTEAMS = get_league_division_team_data()

    p.add('-c',
          '--config',
          required=False,
          is_config_file=True,
          help='config file path')

    # Winning streaks or losing streaks
    g = p.add_mutually_exclusive_group()
    g.add('--winning',
          action='store_true',
          default=False,
          help='Find winning streaks')
    g.add('--losing',
          action='store_true',
          default=False,
          help='Find losing streaks')

    # Pick our team
    h = p.add_mutually_exclusive_group()
    h.add('--team',
          choices=ALLTEAMS,
          action='append',
          help='Specify our team (use flag multiple times for multiple teams)')
    h.add('--division',
          choices=DIVISIONS,
          action='append',
          help='Specify our division (use flag multiple times for multiple divisions)')
    h.add('--league',
          choices=LEAGUES,
          action='append',
          help='Specify our league')

    # Pick versus team
    k = p.add_mutually_exclusive_group()
    k.add('--versus-team',
          choices=ALLTEAMS,
          action='append',
          help='Specify versus team (use flag multiple times for multiple teams)')
    k.add('--versus-division',
          choices=DIVISIONS,
          action='append',
          help='Specify versus division (use flag multiple times for multiple divisions)')
    k.add('--versus-league',
          choices=LEAGUES,
          action='append',
          help='Specify versus league')

    # Specify what season data to view
    p.add('--season',
          required=False,
          action='append',
          choices=['1', '2', '3', '4', '5'],
          help='Specify season (use flag multiple times for multiple seasons, no --seasons flag means all data)')

    # Minimum number of wins to be considered a streak
    p.add('--min',
          required=False,
          type=int,
          default=3,
          help='Minimum number of wins to be considered a streak (defaults to 3, make this higher if looking at multiple teams)')

    p.add('--html',
          action='store_true',
          default=False,
          help='Print streak data in HTML format')
    p.add('--output',
          required=False,
          type=str,
          default='',
          help='Specify the name of the HTML output file, for use with --html flag')

    # Pick format for streak data
    m = p.add_mutually_exclusive_group()
    m.add('--long',
          action='store_true',
          default=False,
          help='Print streak data in long format (one table per streak)')
    m.add('--short',
          action='store_true',
          default=False,
          help='Print streak data in short format (one line per streak)')

    # Pick name format (nickname vs full name)
    m = p.add_mutually_exclusive_group()
    m.add('--nickname',
          action='store_true',
          default=False,
          help='Print team nicknames (e.g., Sunbeams)')
    m.add('--fullname',
          action='store_true',
          default=False,
          help='Print full team names (e.g., Hellmouth Sunbeams)')

    # Parse arguments
    options = p.parse_args(sys.argv[1:])

    # If user did not specify winning/losing, use default (winning)
    if (not options.winning) and (not options.losing):
        options.winning = True

    # If the user did not specify long/short table format, use default (short)
    if (not options.long) and (not options.short):
        options.short = True

    # If user did not specify a name format, use short
    if (not options.nickname) and (not options.fullname):
        options.nickname = True

    # Make sure output file is an absolute path
    if options.output != '':
        options.output = os.path.abspath(options.output)

    # If the user specified a division or a league,
    # turn that into a list of teams for them
    if options.division:
        divteams = []
        for div in options.division:
            divteams += division_to_teams(div)
        options.team = divteams
        options.division = None
    if options.league:
        leateams = []
        for lea in options.league:
            leateams += league_to_teams(lea)
        options.team = leateams
        options.league = None
    # Same for versus
    if options.versus_division:
        vdivteams = []
        for div in options.versus_division:
            vdivteams += division_to_teams(div)
        options.versus_team = vdivteams
        options.versus_division = None
    if options.versus_league:
        vleateams = []
        for lea in options.versus_league:
            vleateams += league_to_teams(lea)
        options.versus_team = vleateams
        options.versus_league = None

    # If nothing was supplied for our team/division/league, use all teams
    if not options.team and not options.division and not options.league:
        options.team = ALLTEAMS

    # If nothing was supplied for versus team/division/league, use all teams
    if not options.versus_team and not options.versus_division and not options.versus_league:
        options.versus_team = ALLTEAMS

    # If nothing was provided for seasons, set it to 'all'
    if not options.season:
        options.season = ['all']

    # No more user input required, so convert Dale back to utf8
    options.team = [desanitize_dale(s) for s in options.team]
    options.versus_team = [desanitize_dale(s) for s in options.versus_team]

    if options.html:
        v = HtmlView(options)
        v.table()
    else:
        v = TextView(options)
        v.table()


def get_league_division_team_data():
    """
    Get a list of leagues, divisions, and teams.
    This is for use in creating CLI flag values,
    so we replace Dal\u00e9 with Dale.
    """
    with open(TEAMS_DATA_JSON, 'r') as f:
        td = json.load(f)
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
    with open(TEAMS_DATA_JSON, 'r') as f:
        td = json.load(f)
    teams = []
    teams += td['leagues'][league]
    teams = [sanitize_dale(s) for s in teams]
    return teams


def division_to_teams(division):
    """
    For a given division, return a list of all teams in that league.
    We replace Dal\u00e9 with Dale (see above).
    """
    with open(TEAMS_DATA_JSON, 'r') as f:
        td = json.load(f)
    teams = []
    teams += td['divisions'][division]
    teams = [sanitize_dale(s) for s in teams]
    return teams


if __name__ == '__main__':
    main()
