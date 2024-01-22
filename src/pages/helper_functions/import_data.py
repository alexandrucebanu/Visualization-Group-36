import os
import pandas as pd
import re

def getAgeYears(ageString):
    return int(ageString.split('-')[0])


def importData():

    # TODO: wrap the generation of the merged dataset with a separate module/function.
    files = ["player_shooting.csv", "player_defense.csv", "player_gca.csv", "player_possession.csv", "player_playingtime.csv", "player_passing.csv", "player_passing_types.csv", "player_misc.csv"]
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
    external = external[['short_name', 'long_name', 'wage_eur', 'value_eur', 'preferred_foot',
        'movement_sprint_speed', 'movement_reactions',
        'power_jumping', 'power_stamina']]
    external = external.drop_duplicates(subset='long_name')
    external = external.drop_duplicates(subset='short_name')
    external = external.reset_index()

    # Impute NA's in the wage_eur with the mean
    mean_wage = sourceDF['wage_eur'].mean()
    sourceDF['wage_eur'] = sourceDF['wage_eur'].fillna(mean_wage)
    sourceDF['wage_eur'] = sourceDF['wage_eur'].astype(int)

    # ========================
    # Merge the two dataframes    
    # ========================
    name_list = []
    not_seen = []
    for player_name in sourceDF['player']:
        short_name_ = False
        long_name_ = False
        if (len(player_name.split()) == 1):
            for short_name in external['short_name']:
                if short_name == player_name:
                    name_list.append(short_name)
                    short_name_ = True
                    break
        
        if short_name_ == False:
            for long_name in external['long_name']:
                if all((name in long_name) for name in player_name.split()):
                    name_list.append(long_name)
                    long_name_ = True
                    break
        
        if (short_name_ == False) and (long_name_ == False):
            not_seen.append(player_name)
            name_list.append(0)
    
    name_list_ex = []
    for i in range(0, len(external)):
        if external.loc[i, 'short_name'] in name_list:
            name_list_ex.append(external.loc[i, 'short_name'])
        elif external.loc[i, 'long_name'] in name_list:
            name_list_ex.append(external.loc[i, 'long_name'])
        else:
            name_list_ex.append('No match')

    sourceDF['name'] = name_list
    external['name'] = name_list_ex

    add_list = []
    for name in name_list:
        if name in name_list_ex:
            add_list.append(0)
        else:
            add_list.append(1)

    #sourceDF['short_name'] = sourceDF['player'].str.replace(r'^(\w)\w*\s', r'\1. ')
    sourceDF = sourceDF.merge(external, on='name', how='left')
    sourceDF = sourceDF.drop('name', axis=1)

    # Write to csv
    filePath = os.path.join(os.path.dirname(__file__), ('../../data/' + 'merged_data.csv'))
    sourceDF.to_csv(filePath)

    filePath = os.path.join(os.path.dirname(__file__), ('../../data/' + 'merged_data.csv'))
    frame = pd.read_csv(filePath, index_col=0)

importData()
