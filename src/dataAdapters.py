import pandas as pd
import pycountry
from typing import Union
import os
from PIL import Image
import re
import dash
import urllib.parse
import unicodedata
from pathlib import Path


<<<<<<< HEAD
def getTeamGroup(team: str, mapToLetters=False) -> Union[int, str]:
=======
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
>>>>>>> general_plots
    """
    :type team: int | str <- The input team (either in the group number of the corresponding letter in uppercase)
    :rtype: int <- The letter representing the group the team belongs to | returns 0 if the team group could not be found
    """
    team = team.capitalize()
    print('team: ', team)
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
    :rtype: str | bool <- The name of player's team in the games | returns False in case the player couldn't be found in the source dataset (players_misc.csv)
    :type playerName: str <- The name of the player to retrieve the team for
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

    :param s: The input string
    :type s: str
    :return: A list of comparable items, including numeric parts
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
    Generate the directory path for a player's player_images.

    :param playerName: The name of the player
    :type playerName: str
    :param playerTeam: The name of the player's team
    :type playerTeam: str
    :param playerGroup: The name of the player's team group
    :type playerGroup: str
    :return: The directory path for the player's player_images
    :rtype: str
    """
    try:
        if not playerTeam:
            # In case the name of the player team is not provided, getPlayerTeam() is used to look it up
            playerTeam = getPlayerTeam(playerName)
        if not playerGroup:
            print('group: ', playerGroup)
            # In case the name of the player team group is not provided, playerTeam() is used to look it up
            playerGroup = getTeamGroup(playerTeam, mapToLetters=True)

        # Handle exceptions here if needed
        # TODO: handle exceptions <- IR Iran for example

        print(f"Player: {playerName}, Team: {playerTeam}, Group: {playerGroup}")

        # formatted_player_name = playerName.encode('unicode-escape').decode('utf-8')
        directory_path = f"assets/player_images/Group {playerGroup}/{playerTeam} Players/Images_{playerName}"

        # Check if the directory exists, otherwise display 'unknown_user2.png'
        print('2839ns', directory_path)

        if os.path.exists(directory_path):
            return directory_path
        else:
            return "icons/unknown_user_left.svg"
    except Exception as e:
        print(f"Error generating player image directory: {e}")
        return "icons/unknown_user_left.svg"


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


print(playerImageDirectory("Aaron Ramsey"))