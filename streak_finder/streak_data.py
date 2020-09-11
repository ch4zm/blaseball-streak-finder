import os
import pandas as pd
import blaseball_core_game_data as gd


"""
The StreakData class wraps a data frame with all the game data
in it. You can then ask it to give you streak information,
and it will do the necessary calculations and return the
necessary information.
"""


class NoStreaksException(Exception):
    pass

class StreakData(object):
    """
    Class representing a data frame with game data.
    """
    def __init__(self, options):
        """Load the data set into self.df"""
        self.df = pd.read_json(json.loads(gd.get_games_data()))

        # Drop tie games
        self.df = self._filter_ties()

        # Fiter data based on seasons provided by user (and store seasons for later)
        self.df, self.seasons = self._season_filter_df(options.season)

        # Winning or losing streak
        self.winning = options.winning

        # Min number of wins for streak
        self.min = options.min

        # Get all data about games with our teams and versus teams
        # (Creates dictionary with team name-team df as the k-v pairs)
        self.our_teams = options.team
        self.their_teams = options.versus_team

        if self.winning:
            self.our_key = 'winningTeamNickname'
            self.their_key = 'losingTeamNickname'
        else:
            self.our_key = 'losingTeamNickname'
            self.their_key = 'winningTeamNickname'

    def _filter_ties(self):
        mask = self.df.loc[self.df['homeScore']!=self.df['awayScore']]
        return mask

    def _season_filter_df(self, user_input_seasons):
        """
        Filter game data on season number(s).
        The seasons provided in the input are one-indexed.
        The dataframe's season numbers (from the blaseball.com API) are zero-indexed.
        """
        if 'all' in user_input_seasons:
            # Get all unique 0-indexed season values
            seasons = list(set(self.df['season'].values))
        else:
            # User provides 1-indexed season values, so convert to 0-indexed
            seasons = [int(s)-1 for s in user_input_seasons]
        mask = self.df.loc[self.df['season'].isin(seasons)]
        return mask, seasons

    def find_streaks(self):
        """
        Find streaks, compile a dataframe with streak info,
        and return it along with team name-team game data dict.
        """
        # Filter step
        our_data = self.filter_step(self.our_teams, self.their_teams)
        # Data aggregation step
        streak_df = self.aggregate_step(our_data)

        return (streak_df, our_data)

    def filter_step(self, our_teams, their_teams):
        """
        Filter game data on team(s)
        """
        our_key = self.our_key
        their_key = self.their_key
        our_data = {}
        for our_team in our_teams:
            our_mask = (self.df[our_key]==our_team) & (self.df[their_key].isin(their_teams))
            their_mask = (self.df[our_key].isin(their_teams)) & (self.df[their_key]==our_team)
            our_df = self.df.loc[our_mask | their_mask]
            our_data[our_team] = our_df
        return our_data

    def aggregate_step(self, our_data):
        """
        Aggregate wins into streaks, and return a data frame with streak info
        """
        our_key = self.our_key
        their_key = self.their_key
        for our_team in self.our_teams:
            our_df = our_data[our_team]
            if our_df.shape[0]==0:
                continue

            # Create a column: partOfStreak
            # 0 indicates streak is broken, 1 indicates streak is going
            postreak_lambda = lambda row: 1 if row[our_key]==our_team else 0
            postreak_col = our_df.apply(postreak_lambda, axis=1)
            our_df = our_df.assign(**{'partOfStreak': postreak_col.values})
            our_data[our_team] = our_df

        # As we find streaks, add them to a dataframe with colums:
        # - Streaking Team Name (str)
        # - Streak Length (int)
        # - Streak Days (list)
        streaks = pd.DataFrame()

        for our_team in self.our_teams:
            our_df = our_data[our_team]

            # Need to iterate over each season
            #this_season = self.seasons[0]
            for this_season in self.seasons:

                our_season_df = our_df.loc[our_df['season']==this_season]

                streak_length = 0
                streak_days = []
                for i, row in our_season_df.iterrows():
                    # Note: we need to handle multiple seasons
                    # Either we filter the DF and iterate over unique season values here,
                    # or we do it somewhere else...
                    # What about teams? Do we iterate over teams?
                    if row['partOfStreak']==1:
                        # The streak continues!
                        # Increase streak counter by 1
                        streak_length += 1
                        streak_days.append(row['day'])
                    else:
                        # End of the streak
                        if len(streak_days)>=self.min:
                            # Add it to a new row in our streaks dataframe
                            new_row = pd.DataFrame({
                                "Team Name": our_team,
                                "Streak Length": streak_length,
                                "Streak Season": this_season,
                                "Streak Start": streak_days[0], # makes sorting easier
                                "Streak Days": [streak_days]
                            })
                            streaks = streaks.append(new_row)
                        # Reset
                        streak_length = 0
                        streak_days = []
        if streaks.shape[0]==0:
            raise NoStreaksException("No streaks found")
        streaks = streaks.sort_values(['Streak Length', 'Streak Season', 'Streak Start'], ascending=[False, True, True])
        return streaks

