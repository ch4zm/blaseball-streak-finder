import os
import sys
from .util import sanitize_dale, get_short2long, get_league_division_team_data
from .streak_data import StreakData, NoStreaksException


class View(object):
    """
    Base class for view classes, so that all they have to do
    is define a short_table and long_table method.
    """
    def __init__(self, options):
        self.short = options.short
        self.winning = options.winning
        self.use_nicknames = options.nickname
        self.our_teams = options.team
        self.their_teams = options.versus_team
        self.min = options.min
        self.seasons = options.season
        _, _, self.ALLTEAMS = get_league_division_team_data()

        self.streak_data = StreakData(options)

    def make_table_descr(self):
        """Assemble a brief description to put ahead of all of the tables""" 
        descr = ""
        if self.winning:
            descr = "Winning "
        else:
            descr = "Losing "
        descr += "streaks "

        # Sanitize unicode for and comparison
        our_teams = [sanitize_dale(t) for t in self.our_teams]
        their_teams = [sanitize_dale(t) for t in self.their_teams]

        # State minimum number of games in this table
        if self.min:
            descr += "of %d or more games "%(self.min)

        # If our_teams is all teams, just say all teams
        if len(set(self.ALLTEAMS) - set(our_teams)) == 0:
            our_teams = ["all teams"]
        if len(set(self.ALLTEAMS) - set(their_teams)) == 0:
            their_teams = ["all teams"]
        descr += "for %s versus %s "%(", ".join(our_teams), ", ".join(their_teams))

        # for season X
        if 'all' in self.seasons:
            descr += "for all time"
        elif len(self.seasons)==1:
            descr += "for season %s"%("".join([str(j) for j in self.seasons]))
        else:
            descr += "for seasons %s"%(", ".join([str(j) for j in self.seasons]))

        return descr

    def short_table(self):
        """Virtual method to print a short table summarizing streaks found"""
        raise NotImplementedError("View class is a base class and does not implement short_table")

    def long_table(self):
        """Virtual method to print tables with details about streaks found"""
        raise NotImplementedError("View class is a base class and does not implement long_table")

    def table(self):
        if self.short:
            self.short_table()
        else:
            self.long_table()


class TextView(View):
    """
    TextView turns a dataframe into text tables.
    """
    def short_table(self):
        """
        Print a short table that summarizes all of the streaks found.
        One line/row per streak.
        """
        # Team nickname to full name map
        short2long = get_short2long()

        try:
            streak_df, _ = self.streak_data.find_streaks()
        except NoStreaksException:
            print("\nNo streaks matching the specified criteria were found. Try a lower value for --min, or more versus teams.\n")
            sys.exit(0)

        # For new columns
        nickfull = lambda x: x if self.use_nicknames else short2long[x]

        # Nicknames or full names
        streak_df['Team Name'] = streak_df['Team Name'].apply(nickfull)

        table = []

        str_template = "%-25s %-9s %-9s %s"
        head = str_template%("Team Name", "Length", "Season", "Days")
        line = "-"*60
        table_descr = self.make_table_descr()

        table.append("\n" + table_descr + "\n")
        table.append(head)
        table.append(line)
        for i, row in streak_df.iterrows():
            row = str_template%(
                row['Team Name'],
                row['Streak Length'],
                int(row['Streak Season'])+1,
                ", ".join([str(j+1) for j in row['Streak Days']])
            )
            table.append(row)

        table_descr = self.make_table_descr()
        print("\n".join(table))
        print("\nNote: all days and seasons displayed are 1-indexed.")

    def long_table(self):
        """
        Print a set of tables that summarize all games in the streaks found.
        One table per streak, one row per game that is part of the streak.
        """
        # Team nickname to full name map
        short2long = get_short2long()

        try:
            streak_df, our_data = self.streak_data.find_streaks()
        except NoStreaksException:
            print("\nNo streaks matching the specified criteria were found. Try a lower value for --min, or more versus teams.\n")
            sys.exit(0)

        # Table description (head matter)
        table_descr = self.make_table_descr()
        print("\n" + table_descr)

        # Create one table per streak found
        line = "-"*60
        scorestring = "G%d: Season %d Game %d: %s %-2d @ %2d %s"
        for i, (_, row) in enumerate(streak_df.iterrows()):
            wl = "Winning" if self.winning else "Losing"
            our_team = row['Team Name']
            our_df = our_data[our_team]

            table = []
            table.append("\n\n")
            table.append(line)
            table.append("%d Game %s Streak"%(row['Streak Length'], wl))
            if self.use_nicknames:
                tname = row['Team Name']
            else:
                tname = short2long[row['Team Name']]
            table.append("%s"%(tname))
            table.append("Season %d Games %s"%(row['Streak Season']+1, ", ".join([str(j) for j in row['Streak Days']])))
            table.append(line)

            for j, today in enumerate(row['Streak Days']):
                this_season = int(row['Streak Season'])
                temp = our_df.loc[(our_df['day']==today) & (our_df['season']==this_season)]
                if self.use_nicknames:
                    home_name_key = 'homeTeamNickname'
                    away_name_key = 'awayTeamNickname'
                else:
                    home_name_key = 'homeTeamName'
                    away_name_key = 'awayTeamName'
                table.append(scorestring%(
                    j+1,
                    temp['season']+1,
                    temp['day']+1,
                    temp[away_name_key].values[0],
                    temp['awayScore'].values[0],
                    temp['homeScore'].values[0],
                    temp[home_name_key].values[0]
                ))
            table.append(line)
            table.append("\n")

            print("\n".join(table))

        # Note to user (foot matter)
        print("\nNote: all days and seasons displayed are 1-indexed.")



class MarkdownView(View):
    """
    MarkdownView turns a dataframe into Markdown tables.
    """
    def __init__(self, options):
        super.__init__(options)

        if options.output == '':
            self.output_file = None
        else:
            self.output_file = options.output
            if os.path.exists(self.output_file):
                print("WARNING: Overwriting an existing file %s"%(self.output_file))
                print("Waiting 5 seconds before proceeding")
                time.sleep(5)
                # Clear out the file
                with open(self.output_file, 'w') as f:
                    f.write("")
            else:
                output_file_path = os.path.dirname(self.output_file)
                if not os.path.exists(output_file_path):
                    raise Exception("Error: directory for output file (%s) does not exist!"%(output_file_path))

    def short_table(self):
        """
        Print a short table that summarizes all of the streaks found.
        One line/row per streak.
        """
        # Team nickname to full name map
        short2long = get_short2long()

        try:
            streak_df, _ = self.streak_data.find_streaks()
        except NoStreaksException:
            print("\nNo streaks matching the specified criteria were found. Try a lower value for --min, or more versus teams.\n")
            sys.exit(0)

        # For new columns
        nickfull = lambda x: x if self.use_nicknames else short2long[x]

        # Nicknames or full names
        streak_df['Team Name'] = streak_df['Team Name'].apply(nickfull)

        description = self.make_table_descr()

        # -----

        # This string is the final table in Markdown format
        table = ""

        # Start header line
        table_header = "| Team Name | Length | Season | Days |"
        # Start separator line (controls alignment)
        table_sep = "| ----- | ----- | ----- | ----- |"

        table += table_header
        table += "\n"
        table += table_sep
        table += "\n"
        str_template = "| %-30s | %-10s | %-10s | %s |"
        for i, row in streak_df.iterrows():
            row = str_template%(
                row['Team Name'],
                row['Streak Length'],
                int(row['Streak Season'])+1,
                ", ".join([str(j+1) for j in row['Streak Days']])
            )
            table += row
            table += "\n"

        if self.output_file is None:
            print("\n\n")
            print(description)
            print("\n\n")
            print(table)
            print("\n")
            print("\nNote: all days and seasons displayed are 1-indexed.")
        else:
            with open(self.output_file, 'w') as f:
                f.write("\n\n")
                f.write(description)
                f.write("\n\n")
                f.write(table)
                f.write("\n")
                f.write("\nNote: all days and seasons displayed are 1-indexed.")


    def long_table(self):
        """
        Print a set of tables that summarize all games in the streaks found.
        One table per streak, one row per game that is part of the streak.
        """
        # Team nickname to full name map
        short2long = get_short2long()

        try:
            streak_df, our_data = self.streak_data.find_streaks()
        except NoStreaksException:
            print("\nNo streaks matching the specified criteria were found. Try a lower value for --min, or more versus teams.\n")
            sys.exit(0)

        # Table description (head matter)
        description = self.make_table_descr()

        # -----

        # This is the master document that compiles all other tables
        md = ""

        # One description for all tables
        md += "\n\n"
        md += description
        md += "\n\n"

        # Create one table per streak found
        for i, (_, row) in enumerate(streak_df.iterrows()):
            # This string is the final table
            table = ""

            wl = "Winning" if self.winning else "Losing"
            short_name = row['Team Name']
            long_name = short2long[short_name]
            if self.use_nicknames:
                this_name = short_name
            else:
                this_name = long_name

            our_df = our_data[short_name]

            table_header = "| %d Game %s Streak by the %s |"%(row['Streak Length'], wl, this_name)
            table_sep = "| ----- |"
            
            row1 = "| Season %d Games %s |"%(row['Streak Season']+1, ", ".join([str(j) for j in row['Streak Days']]))

            table += table_header
            table += "\n"
            table += table_sep
            table += "\n"
            table += row1
            table += "\n"

            scorestring = "| G%d: Season %d Game %d: %s %-2d @ %2d %s |"
            for j, today in enumerate(row['Streak Days']):
                this_season = int(row['Streak Season'])
                temp = our_df.loc[(our_df['day']==today) & (our_df['season']==this_season)]
                if self.use_nicknames:
                    home_name_key = 'homeTeamNickname'
                    away_name_key = 'awayTeamNickname'
                else:
                    home_name_key = 'homeTeamName'
                    away_name_key = 'awayTeamName'
                rowstr = scorestring%(
                    j+1,
                    temp['season']+1,
                    temp['day']+1,
                    temp[away_name_key].values[0],
                    temp['awayScore'].values[0],
                    temp['homeScore'].values[0],
                    temp[home_name_key].values[0]
                )
                table += rowstr
                table += "\n"

            # Add the final table to the master document
            md += table + "\n\n"

        md += "\nNote: all days and seasons displayed are 1-indexed."

        if self.output_file is None:
            print(md)
        else:
            with open(self.output_file, 'w') as f:
                f.write(md)

