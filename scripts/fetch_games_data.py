import re
import os
import requests
import json
import sseclient


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_path = os.path.abspath(os.path.join(root_path, 'cli', 'data'))

GAMES_DATA_JSON = os.path.join(data_path, "games_data_trim.json")
UPDATE_DATA_JSON = os.path.join(data_path, "update_data.json")


def main():
    print("Loading data")
    gameData, updateData = load_game_data()

    lastDate = updateData["lastDate"]
    print(f"Last date found was season {lastDate[0] + 1}, day {lastDate[1] + 1}")

    currDate = get_game_day()
    print(f"Current date is season {currDate[0] + 1}, day {currDate[1] + 1}")

    missingDays = find_missing_days(lastDate, currDate)

    print(f"It appears we're missing {len(missingDays)} days.")

    if(len(missingDays) > 0):
        print("Attempting to fetch intermediate games.")
        for date in missingDays:
            print(f"Fetching season {date[0] + 1}, day {date[1] + 1}")
            if(date in updateData["gameDates"]):
                # If we already have this date, drop it and re-download it
                print("Odd... we already have that day? Replacing it for safety.")
                gameData = [game for game in gameData if (game["season"] != date[0] or game["day"] != date[1])]
            # Get the game data and postprocess it
            result = requests.get(f'https://www.blaseball.com/database/games?day={date[1]}&season={date[0]}')
            result = result.json()
            post_result = postprocess_game_data(result)
            for game in post_result:
                gameData.append(game)
            updateData["lastDate"] = date
            updateData["gameDates"].append(date)
            # Save to file each time (slower but safer)
            save_game_data(gameData, updateData)


def postprocess_game_data(gameData):
    """Add derived quantities to make filtering easier"""
    # Load emoji data that will be useful for 2 columns

    trimGameData = []
    for game in gameData:
        trim = {}

        # For each game, create a new version of the game data
        # that drops extraneous keys, copies useful keys,
        # and creates new useful keys to view data by winner/loser
        # in addition to home/away.

        # Keys to keep:
        keep_keys = [
            'id',
            'season',
            'day',
            'awayOdds',
            'awayPitcherName',
            'awayScore',
            'awayTeamEmoji',
            'awayTeamName',
            'awayTeamNickname',
            'homeOdds',
            'homePitcherName',
            'homeScore',
            'homeTeamEmoji',
            'homeTeamName',
            'homeTeamNickname',
            'isPostseason',
            'shame'
        ]
        for key in keep_keys:
            trim[key] = game[key]

        # Keys to add:
        add_keys = ['TeamName', 'TeamNickname', 'TeamEmoji', 'Score', 'Odds', 'PitcherName']
        for key in add_keys:
            # Assign winning/losing a value from home/away as appropriate
            winning_key = "winning" + key
            losing_key = "losing" + key
            home_key = "home" + key
            away_key = "away" + key
            trim[winning_key] = game[home_key] if game['homeScore'] > game['awayScore'] else game[away_key]
            trim[losing_key] = game[home_key] if game['homeScore'] < game['awayScore'] else game[away_key]

        # add more keys here (hard-coded formulas)
        trim['runDiff'] = abs(game['homeScore'] - game['awayScore'])
        trim['whoWon'] = 'home' if game['homeScore'] > game['awayScore'] else 'away'

        trimGameData.append(trim)

    return trimGameData


def get_game_day():
    client = sseclient.SSEClient("https://www.blaseball.com/events/streamData")
    singleEvent = next(client) #.events())
    sim = json.loads(singleEvent.data)["value"]["games"]["sim"]
    print("season %s\nday %s"%(sim["season"], sim["day"]))
    return (sim["season"], sim["day"])


def load_game_data():
    gameDates = []
    try:
        with open(GAMES_DATA_JSON, "r") as f:
            gameData = []
            arr = json.load(f)
            for game in arr:
                gameData.append(game)
                gameDates.append((game['season'], game['day']))
    except FileNotFoundError:
        gameData = []

    try:
        with open(UPDATE_DATA_JSON, "r") as f:
            updateData = json.loads(f.read())
    except FileNotFoundError:
        updateData = {"lastDate": (0, 0)}

    updateData["gameDates"] = gameDates
    return (gameData, updateData)


def save_game_data(gameData, updateData):
    with open(GAMES_DATA_JSON, "w") as f:
        json.dump(gameData, f)
        # This makes the json data readable:
        #json.dump(gameData, f, indent=4, sort_keys=True)

    with open(UPDATE_DATA_JSON, "w") as f:
        json.dump(updateData, f, sort_keys=True)


def find_missing_days(lastDate, currDate):
    # Find out which day's we're missing
    missingDays = []
    if(lastDate[0] < currDate[0]):
        for season in range(lastDate[0], currDate[0]):
            if(season == lastDate[0]):
                lastDay = lastDate[1]
            else:
                lastDay = 0
            for day in range(lastDay, 115):
                missingDays.append((season, day))
        lastDay = -1
    if(lastDate[0] == currDate[0]):
        lastDay = lastDate[1]
    for day in range(lastDay + 1, currDate[1]):
        missingDays.append((currDate[0], day))
    return missingDays


if __name__ == "__main__":
    main()
