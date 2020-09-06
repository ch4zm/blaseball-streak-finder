# blaseball-streak-finder

This repo contains a command line tool called `streak-finder`
that helps find blaseball winning and losing streaks.

You can use command line flags or configuration options to filter
on conditions, including:

* Season
* At home or away
* Streaks versus a team, division, or league
* Streaks versus a pitcher

This allows you to find not just winning and losing streaks, but also
winning and losing streaks _against a set of opponents_.


## Screenshots

The `streak-finder` tool can print plain text tables to the console,
or output tables in HTML format. Here are a few examples:

Look for winning streaks from the Tigers from Season 3 and 4,

![Winning streaks for Tigers Seasons 3 and 4](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/s34tigers.png)

Compare to winning streaks by the Pies at the same:

![Winning streaks for Tigers and Pies Seasons 3 and 4](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/s34tigerspies.png)

Show the top winning streaks in Season 1 for the Good League:

![Winning streaks for Good League Season 1](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/goodleaguestreaks.png)

Compare to top winning streaks in Season 1 for the Evil League:

![Winning streaks for Evil League Season 1](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/evilleaguestreaks.png)

Show game-by-game summaries of the worst losing streaks in blaseball history:

![Worst losing streaks](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/worstdetailsnew.png)

This tool also works on antique hardware!

![Worst losing streaks antique hardware](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/worstdetailsold.png)

The tool also offers the ability to export tables in HTML format,
in both short and long versions:

![HTML short command](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/htmlshort.png)

![HTML short page](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/htmlshortpage.png)

![HTML long command](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/htmllong.png)

![HTML long page](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/htmllongpage.png)

## Installation

### pip

```
pip install blaseball-streak-finder
```

### source

Start by cloning the package:

```
git clone https://github.com/ch4zm/blaseball-streak-finder
cd blaseball-streak-finder
```

If installing from source, it is recommended you install the package
into a virtual environment. For example:

```
virtualenv vp
source vp/bin/activate
```

Now build and install the package:

```
python setup.py build
python setup.py install
```

Now test that the tool is available on the command line, and try out
a command to search for some streaks:

```
which streak-finder
streak-finder --min 8 --short
```

## Quick Start

The way this tool works is, it creates a data frame object, applies some filters to it based on command line flags provided
by the user, then runs the data frame through a data viewer (which makes the nice tables). All command line flags can also 
be specified in a config file.

### Command line flags

Command line flags are grouped into data options and view options.

Data options:

* **Winning or Losing Streaks**: Use the `--winning`/`--losing` flags to specify winning/losing streaks

* **Season**: Set season for game data using `--season`. For multiple seasons, repeat the flag: `--season 1 --season 2`

* (Optional) **Our Team**: Specify only one of the following:
    * **Team**: use the `--team` flag to specify the short name of your team (use `--help` to see
      valid choices). For multiple teams, use multiple `--team` flags.
    * **Division**: use the `--division` flag to specify the name of a division. Surround division
      name in quotes, e.g., `--division "Lawful Evil"`
    * **League**: use the `--league` flag to specify the Good/Evil league

* (Optional) **Versus Team**: Specify only one of the following:
    * **Versus Team**: use the `--versus-team` flag to specify the short name of the opposing team (use `--help` to see
      valid choices). For multiple teams, use multiple `--versus-team` flags.
    * **Versus Division**: use the `--versus-division` flag to specify the name of the versus division. Surround division
      name in quotes, e.g., `--versus-division "Lawful Evil"`
    * **Versus League**: use the `--versus-league` flag to specify the versus Good/Evil league

(If neither flag is specified, it will include all games between all teams.)

View options:

* **Minimum**: Specify the minimum number of wins or losses to qualify as a streak with `--min N`

* **HTML**: Use `--html` to specify that the output should be in HTML format.
  If no `--output` file is specified, it will print the HTML to stdout.

* **Output File**: Use `--output` to specify the output file when using the `--html` flag.
  This flag has no effect when `--html` flag is not present.

* **Use Short Output**: Use `--short` to display streaks in short format
  (one line per streak; default option).

* **Use Long Output**: Use `--long` to display streaks in long format
  (one table per streak summarizing each game in the streak).

* **Use Nicknames**: Use `--nickname` flag to use team nicknames in table (e.g., Sunbeams)

* **Use Full Names**: Use `--fullname` flag to use full team name in table (e.g., Hellmouth Sunbeams)

Using a configuration file:

* **Config file**: use the `-c` or `--config` file to point to a configuration file (see next section).


### Configuration file

(Note: several configuration file examples are provided in a section below.)

Every command line flag can be specified in a configuration file as well.
To reproduce the following command line call,

```
streak-finder --season 1 --season 2 --team Tigers --versus-team Pies --min 5 --fullname 
```

we could create a configuration file named `config.ini` with the contents:

```
season = 1
season = 2
team = Tigers
versus-team = Pies
min = 5
fullname = True
```

and run `blaseball-streak-finder` specifying that configuration file:

```
streak-finder --config config.ini
# or
streak-finder -c config.ini
```

This would produce identical output to the command with all the flags.

You can also use both a config file and command line flags; the command line flags will take
precedence over config file options if a parameter is specified by both.


## Data

The data set used by this tool comes from `blaseball.com`'s `/games` API endpoint.
The data set is stored in the json file `cli/data/games_data_trim.json`.


## Configuration Examples

See [`config.example.ini`](https://github.com/ch4zm/blaseball-streak-finder/tree/master/config.example.ini)
in the repo for an example config file.

Show winning streaks from season 3 and season 4 for the Hades Tigers:

```
[data]
season = [3, 4]
team = Tigers
winning
min = 5
```

Include winning streaks by the Pies too:

```
[data]
season = [3, 4]
team = [Tigers, Pies]
winning
min = 5
```

Show the top winning streaks from season 1 for all teams in the Good League:

```
[data]
season = 1
league = Good
winning
min = 7
```

Compare to top winning streaks from season 1 for all teams in the Good League:

```
[data]
season = 1
league = Evil
winning
min = 7
```

Look for losing streaks that were 12 games or more, and print a game-by-game
summary of the streaks using the long format:

```
[data]
min = 12
losing
long
```

Look for winning streaks by the Firefighters that were 7 games or more, and output
the summary table to the file `short.html`:

```
[data]
team = Firefighters
min = 7
winning
short
html
output = short.html
```

Repeat the above streak-finding search, but output a table for each streak
with a game-by-game breakdown (long format) to the file `long.html`:

```
[data]
team = Firefighters
min = 7
winning
long
html
output = long.html
```


## Scripts

This repo includes a script to download game data and reproduce the data set.
The script is intelligent enough to keep track of what days have already been
downloaded, so the first time through it will re-download all game data, but 
from that point forward it will only download game data that has been added
since the last time it was run.

To run the script:

```
python scripts/fetch_game_data.py
```

See the [scripts Readme](scripts/Readme.md) for more info.


## Software architecture

This software consists of three parts:

* The command line flag and config file parser (uses `configargparse` library) - see `cli/command.py`
* The StreakData object that stores the game data in a Pandas data frame (uses `pandas` library) - see
  `cli/streak_data.py`
* The View object that provides a presentation layer on top of the Pandas data frame
  (uses panda's `DataFrame.to_string()` and `DataFrame.to_html()` methods to print the data) - see
  `cli/view.py` (there are two classes, one for plain text and one for HTML)


## Who is this tool for?

This tool is for the blaseball community. It will be useful to people
interested in exploring game data, people who are brainstorming about
lore for their team, and people who are looking for a starting point
for developing their own blaseball tool.


## Future work

* Move data set into a core blaseball game data library

* Win/loss records tool


## Libraries used

This command line tool uses the following libraries under the hood:

* [pandas](https://pandas.pydata.org/) for organizing/filtering data
* [configarparse](https://github.com/bw2/ConfigArgParse) for handling CLI arguments
