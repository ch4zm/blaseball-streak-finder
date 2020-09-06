import json
from blaseball_mike.models import Team

"""
A one-off script to make a dictionary to map
team short names to team long names.

Example:
    Sunbeams -> Hellmouth Sunbeams
"""

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_path = os.path.abspath(os.path.join(root_path, 'cli', 'data'))

OUTPUT_FILE = os.path.join(data_path, 'short2long.json')

def main():
    print("Creating map of team nicknames to full team names")
    all_teams = Team.load_all()
    
    names = {}
    for t in all_teams:
        team = all_teams[t]
        short_name = team.nickname
        long_name = team.full_name
        names[short_name] = long_name
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(names, f)


if __name__=="__main__":
    main()
