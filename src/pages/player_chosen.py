import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import os
import pandas as pd
import dash_bootstrap_components as dbc
from pages.components.general_plots import speed_power_jump, speed_power_jump2

dash.register_page(__name__, path_template='/replace/<player_id>')

# TODO: the following is duplicate. Outsource it.
filePath = os.path.join(os.path.dirname(__file__), '../data/player_gca.csv')
df_defense = pd.read_csv(filePath)


def layout(player_id=None, suppress_callback_exceptions=True):
    if not player_id:
        print('No `player_id` passed...')
        return ""
        # TODO: handle this properly
    player = df_defense.iloc[[player_id]].to_dict(orient='records')[0]

    return [
        html.Div(children=[
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                        'Hi and welcome. You have chosen player with id {}. That would be {}'.format(player_id, player['player'])),
                    ),
                    dbc.Col(
                        html.Div(
                        'These are the position specific plots'),
                    ),
                    dbc.Col(
                        [speed_power_jump,
                        speed_power_jump2,
                        ]
                        #speed_power_jump,
                    ),
                ], justify="evenly",
            ), 
        ])
    ]
