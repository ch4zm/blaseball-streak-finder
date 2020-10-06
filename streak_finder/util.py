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
    tds = json.loads(gd.get_teams_data())

    leagues = set()
    divisions = set()
    teams = set()
    for i in range(len(tds)):
        td = tds[i]
        leagues_ = sorted(list(td['leagues'].keys()))
        divisions_ = sorted(list(td['divisions'].keys()))
        leagues = leagues.union(leagues_)
        divisions = divisions.union(leagues_)

        teams_ = []
        for league_ in leagues_:
            teams_ += td['leagues'][league_]
        teams = teams.union(teams_)

    leagues = sorted(list(leagues))
    teams = sorted(list(teams))
    divisions = sorted(list(divisions))

    return (leagues, divisions, teams)


def league_to_teams(league):
    """
    For a given league, return a list of all teams in that league.
    We replace Dal\u00e9 with Dale (see above).
    """
    tds = json.loads(gd.get_teams_data())
    teams = []
    if season is None:
        for i in range(len(tds)):
            td = tds[i]
            leagues = sorted(list(td['leagues'].keys()))
            if league in leagues:
                teams = sorted(list(td['leagues'][league]))
                break
    else:
        td = tds[season]
        leagues = sorted(list(td['leagues'].keys()))
        if league in leagues:
            teams = sorted(list(td['leagues'][league]))

    if len(teams)==0:
        raise Exception("Error: Could not find any teams in league %s"%(league))
    return teams


def division_to_teams(division):
    """
    For a given division, return a list of all teams in that league.
    We replace Dal\u00e9 with Dale (see above).
    """
    tds = json.loads(gd.get_teams_data())
    teams = []
    if season is None:
        for i in range(len(tds)):
            td = tds[i]
            divisions = sorted(list(td['divisions'].keys()))
            if division in divisions:
                teams = sorted(list(td['divisions'][division]))
                break
    else:
        td = tds[season]
        divisions = sorted(list(td['divisions'].keys()))
        if division in divisions:
            teams = sorted(list(td['divisions'][division]))

    if len(teams)==0:
        raise Exception("Error: Could not find any teams in division %s"%(division))
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



def sanitize_dale(s):
    """Utility function to make CLI flag value easier to set"""
    if s == DALE_UTF8:
        return DALE_SAFE
    elif s== FULL_DALE_UTF8:
        return FULL_DALE_SAFE
    else:
        return s


class CaptureStdout(object):
    """
    A utility object that uses a context manager
    to capture stdout.
    """
    def __init__(self):
        # Boolean: should we pass everything through to stdout?
        # (this object is only functional if passthru is False)
        super().__init__()

    def __enter__(self):
        """
        Open a new context with this CaptureStdout
        object. This happens when we say
        "with CaptureStdout() as output:"
        """
        # We want to swap out sys.stdout with
        # a StringIO object that will save stdout.
        # 
        # Save the existing stdout object so we can
        # restore it when we're done
        self._stdout = sys.stdout
        # Now swap out stdout 
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        """
        Close the context and clean up.
        The *args are needed in case there is an
        exception (we don't deal with those here).
        """
        # Store the result we got
        self.value = self._stringio.getvalue()

        # Clean up (if this is missing, the garbage collector
        # will eventually take care of this...)
        del self._stringio

        # Clean up by setting sys.stdout back to what
        # it was before we opened up this context.
        sys.stdout = self._stdout

    def __repr__(self):
        """When this context manager is printed, it looks like the game ID string"""
        return self.value
