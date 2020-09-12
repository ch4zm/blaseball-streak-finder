import sys
import os
import json
import configargparse
from .view import TextView, HtmlView, MarkdownView
from .util import (
    desanitize_dale,
    get_league_division_team_data,
    league_to_teams,
    division_to_teams
)


def main(sysargs = sys.argv[1:]):

    p = configargparse.ArgParser()

    # These are safe for command line usage (no accent in Dale)
    LEAGUES, DIVISIONS, ALLTEAMS = get_league_division_team_data()

    p.add('-v',
          '--version',
          required=False,
          default=False,
          action='store_true',
          help='Print program name and version number and exit')

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
    p.add('--markdown',
          action='store_true',
          default=False,
          help='Print streak data in Markdown table format')
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

    # -----

    # Parse arguments
    options = p.parse_args(sys.argv[1:])

    # If the user asked for the version,
    # print the version number and exit.
    if options.version:
        from . import _program, __version__
        print(_program, __version__)
        sys.exit(0)

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
    else:
        try:
            _ = [str(j) for j in options.season]
        except ValueError:
            raise Exception("Error: you must provide integers to the --season flag: --season 1 --season 2")

    # No more user input required, so convert Dale back to utf8
    options.team = [desanitize_dale(s) for s in options.team]
    options.versus_team = [desanitize_dale(s) for s in options.versus_team]

    if options.html:
        v = HtmlView(options)
        v.table()
    elif options.markdown:
        v = MarkdownView(options)
        v.table()
    else:
        v = TextView(options)
        v.table()


if __name__ == '__main__':
    main()
