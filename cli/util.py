import json
import os


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = os.path.abspath(os.path.join(root_path, 'data'))

SHORT2LONG_JSON = os.path.join(data_path, "short2long.json")

DALE_SAFE = "Dale" # for command line
DALE_UTF8 = "Dal\u00e9" # for display

FULL_DALE_SAFE = "Miami Dale" # for command line
FULL_DALE_UTF8 = "Miami Dal\u00e9" # for display


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
