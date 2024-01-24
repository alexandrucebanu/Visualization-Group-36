import pandas as pd
import pycountry
from typing import Union
import os
from PIL import Image
import re



def getMergedDataFrame():
    """
    Merges multiple player data CSV files into a single DataFrame.

    :return: The merged DataFrame containing player data from all specified CSV files.
    :rtype: pd.DataFrame
    """
    files = ["player_shooting.csv", "player_possession.csv", "player_playingtime.csv", "player_passing.csv", "player_misc.csv"];
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
    Retrieves the group number or letter for a given team.

    :param team: The name of the team.
    :type team: str
    :param mapToLetters: If True, returns the group letter instead of number.
    :type mapToLetters: bool
    :return: The group number or letter for the team.
    :rtype: int | str
    """
    team = team.capitalize()
    # print('team: ', team)
    try:
        group_stats_csv_path = os.path.join(os.path.dirname(__file__), r"data/group_stats.csv")
        df_groups = pd.read_csv(group_stats_csv_path, encoding='utf-8')

        filtered = df_groups[df_groups.team == team]
        groupNumber = int(filtered.group.unique()[0])
        if mapToLetters:
            return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'][groupNumber - 1]
        return groupNumber
    except:
        return 0


def getPlayerTeam(playerName: str) -> Union[str, bool]:
    """
    Retrieves the team name for a given player.

    :param playerName: The name of the player.
    :type playerName: str
    :return: The team name of the player or False if not found.
    :rtype: str | bool
    """
    try:
        players_csv_path = os.path.join(os.path.dirname(__file__), 'data/player_misc.csv')
        df_players = pd.read_csv(players_csv_path, encoding='utf-8')
        filtered = df_players[df_players.player == playerName]
        return (filtered.team.unique()[0])
    except:
        return False


def natural_sort_key(s):
    """
    Generate a key for natural sorting based on numeric values in a string.

    :param s: The input string.
    :type s: str
    :return: A list of comparable items, including numeric parts.
    :rtype: list
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]


def get_first_vertical_image(directory_path):
    """
    Find and return the filename of the first vertical image in the specified directory.

    :param directory_path: The path to the directory containing player_images
    :type directory_path: str
    :return: The filename of the first vertical image, or None if not found
    :rtype: str | None
    """
    try:
        if os.path.isdir(directory_path):
            filenames = sorted(os.listdir(directory_path), key=natural_sort_key)

            for filename in filenames:
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(directory_path, filename)
                    try:
                        img = Image.open(image_path)
                        width, height = img.size

                        # Check if the image is vertically oriented
                        if height > width:
                            encoded_filename = filename.encode('unicode-escape').decode('utf-8')
                            image_path = os.path.join(directory_path.split('assets/', 1)[1], encoded_filename)
                            return image_path
                    except Exception as e:
                        print(f"Error processing image {filename}: {e}")
            return None
        else:
            # If the path is a file, return it directly
            return directory_path
    except Exception as e:
        print(f"Error processing directory {directory_path}: {e}")
        return None


def playerImageDirectory(playerName, playerTeam=None, playerGroup=None):
    """
    Generate the directory path for a player's images.

    :param playerName: The name of the player.
    :type playerName: str
    :param playerTeam: Optional team name of the player.
    :type playerTeam: str
    :param playerGroup: Optional team group of the player.
    :type playerGroup: str
    :return: The directory path for the player's images.
    :rtype: str
    """
    print('name: ', playerName)
    try:
        if not playerTeam:
            # In case the name of the player team is not provided, getPlayerTeam() is used to look it up
            playerTeam = getPlayerTeam(playerName)
        if not playerGroup:
            # In case the name of the player team group is not provided, playerTeam() is used to look it up
            playerGroup = getTeamGroup(playerTeam, mapToLetters=True)

        # Handle exceptions here if needed
        # TODO: handle exceptions <- IR Iran for example

        # formatted_player_name = playerName.encode('unicode-escape').decode('utf-8')
        directory_path = f"assets/player_images/Group {playerGroup}/{playerTeam} Players/Images_{playerName}"

        # Check if the directory exists, otherwise display 'unknown_user2.png'

        if os.path.exists(directory_path):
            return directory_path
        else:
            return None
    except Exception as e:
        print(f"Error generating player image directory: {e}")
        return "icons/player.png"


def getCountryFlagPath(countryName: str):
    """
    Retrieves the file path for a country's flag image based on the country name.

    :param countryName: The name of the country.
    :type countryName: str
    :return: The file path of the country's flag image.
    :rtype: str
    """
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
