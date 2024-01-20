import os
import pandas as pd

def getAgeYears(ageString):
    return int(ageString.split('-')[0])

def importData():

    # TODO: wrap the generation of the merged dataset with a separate module/function.
    files = ["player_shooting.csv", "player_defense.csv", "player_gca.csv", "player_possession.csv", "player_playingtime.csv", "player_passing.csv", "player_misc.csv"]
    # TODO: bug: when including player_gca.csv the df will be sliced (as there are only 41 rows there) and we merge with it.
    frames = []

    counter = 0
    for file in files:
        filePath = os.path.join(os.path.dirname(__file__), ('../../data/' + file))
        frame = pd.read_csv(filePath)
        frames.append(frame)
    sourceDF = frames[0]
    for i in range(1, len(frames)):
        sourceDF = pd.merge(sourceDF, frames[i])

    sourceDF['age'] = (sourceDF['age']).map(getAgeYears)  # This is the dataframe form which the plots are being applied. Applying filters will limit the rows in this object.

    # Merge data with external source
    external = pd.read_csv(os.path.join(os.path.dirname(__file__), ('../../data/' + 'players_22.csv')))
    external = external[['short_name', 'wage_eur', 'value_eur', 'preferred_foot',
                            'movement_sprint_speed', 'movement_reactions',
                            'power_jumping', 'power_stamina']]
    external = external.drop_duplicates(subset='short_name')
    sourceDF['short_name'] = sourceDF['player'].str.replace(r'^(\w)\w*\s', r'\1. ')
    sourceDF = sourceDF.merge(external, on='short_name', how='left')
    sourceDF = sourceDF.drop('short_name', axis=1)

    return sourceDF

