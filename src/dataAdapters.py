import pandas as pd
import os
import pycountry


def getMergedDataFrame():
    files = ["player_shooting.csv", "player_possession.csv", "player_playingtime.csv", "player_passing.csv",
             "player_misc.csv"];
    frames = []

    counter = 0
    for file in files:
        filePath = os.path.join(os.path.dirname(__file__), ('data/' + file))

        frame = pd.read_csv(filePath)
        frames.append(frame)
        df = frames[0]
        for i in range(1, len(frames)):
            df = pd.merge(df, frames[i])
    return df


def getTeamGroup(team: str, mapToLetters=False) -> int | str:
    """
    :type team: int | str <- The input team (either in the group number of the corresponding letter in uppercase)
    :rtype: int <- The letter representing the group the team belongs to | returns 0 if the team group could not be found
    """
    team = team.capitalize()
    try:
        group_stats_csv_path = os.path.join(os.path.dirname(__file__), 'data/group_stats.csv')
        df_groups = pd.read_csv(group_stats_csv_path)

        filtered = df_groups[df_groups.team == team]
        groupNumber = int(filtered.group.unique()[0])
        if mapToLetters:
            return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'][groupNumber - 1]
        return groupNumber
    except:
        return 0


def getPlayerTeam(playerName: str) -> str | bool:
    """
    :rtype: str | bool <- The name of player's team in the games | returns False in case the player couldn't be found in the source dataset (players_misc.csv)
    :type playerName: str <- The name of the player to retrieve the team for
    """
    try:
        players_csv_path = os.path.join(os.path.dirname(__file__), 'data/player_misc.csv')
        df_players = pd.read_csv(players_csv_path)
        filtered = df_players[df_players.player == playerName]
        return (filtered.team.unique()[0])
    except:
        return False


def playerImageDirectory(playerName, playerTeam=None, playerGroup=None):
    if not playerTeam:
        # In case the name of the player team is not provided, `getPlayerTeam()` is used to look it up
        playerTeam = getPlayerTeam(playerName)
    if not playerGroup:
        # In case the name of the player team group is not provided, `playerTeam()` is used to look it up
        playerGroup = getTeamGroup(playerTeam, mapToLetters=True)

    # TODO: handle exceptions <- IR Iran for example

    return "GROUP {}/{} Players/Images_{}".format(playerGroup, playerTeam, playerName)


def getCountryFlagPath(countryName: str):
    countryCode = "un"

    # manually handling the countries with unlisted names | TODO: do this better with dictionary (using dict.keys() probably)
    if countryName == "IR Iran":
        countryCode = "ir"
    elif countryName == "Wales":
        countryCode = "gb-wls"
    elif countryName == "England":
        countryCode = "gb-eng"
    elif countryName == "Korea Republic":
        countryCode = "kr"
    else:
        country = pycountry.countries.get(name=countryName)
        if country:
            countryCode = country.alpha_2.lower()
    return "flags/{}.png".format(countryCode)
