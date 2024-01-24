"""
-> The purpose of this script is to limit the number of flags in `src/assets/flag` to the countries which appear in our dataset.
-> The original collection of flags from [`hampusborgos/country-flags`](https://github.com/hampusborgos/country-flags) consists of 255 flag image files which is a great number to be stored in the repository
-> It's recommended to run this script once when initializing the app (most likely in the development phase) as a one-time operation.
"""

import os
import pandas as pd
import pycountry

group_stats_csv_path = os.path.join(os.path.dirname(__file__), '../data/player_misc.csv')
print(group_stats_csv_path)
df_groups = pd.read_csv(group_stats_csv_path)

countries = df_groups.team.unique()

allFlags = os.listdir(os.path.join(os.path.dirname(__file__), "../assets/flags"))

# manually exempting the country flags with names no in the dataset
exemptions = ["gb-wls.png", "ir.png", "kr.png", "gb-eng.png"]

# Loop through the countries in the dataset and exempt their corresponding flags from deletion
for country in countries:
    try:
        exemptions.append(pycountry.countries.get(name=country).alpha_2.lower() + ".png")
    except:
        print("Not exempting: ", country)
        continue

# Remove flag files that are not in the exemptions list
for flagFile in allFlags:
    if flagFile in exemptions:
        continue
    else:
        filePath = os.path.join(os.path.dirname(__file__), "../assets/flags/" + flagFile)
        os.remove(filePath)
