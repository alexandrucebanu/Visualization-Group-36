import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import os
import pandas as pd
from components import specific_players

dash.register_page(__name__, path_template='/replace/<player_id>')

# TODO: the following is duplicate. Outsource it.
filePath = os.path.join(os.path.dirname(__file__), '../data/player_gca.csv')
df_defense = pd.read_csv(filePath)


def layout(player_id=None):
    if not player_id:
        print('No `player_id` passed...')
        return ""
        # TODO: handle this properly
    player = df_defense.iloc[[player_id]].to_dict(orient='records')[0]

    return specific_players.specific_plots_component
