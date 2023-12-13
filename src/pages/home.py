import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os

dash.register_page(__name__, path='/')

# TODO: team data placement instruction in README.md <- We're using `group_stats.csv` right now
# TODO: generate a catch for when the data directory does not exist

filePath = os.path.join(os.path.dirname(__file__), '../data/player_gca.csv')
df_defense = pd.read_csv(filePath)
playerNames = df_defense.player.unique()

layout = [
    html.Div([
        html.Div(id='search_box_header', style={'background': (
            'linear-gradient(rgba(255,255,255,0), rgba(0,0,0,0.65)), url({}) center'.format(
                dash.get_asset_url('backgrounds/soccer_field.jpg')))}),
        html.Div(id='logo',
                 style={'background': 'url(' + dash.get_asset_url('icons/icons8-soccer-94.png') + ')'}),

        html.H1('Welcome to Stratinder', style={'color': '#243E4C', 'display': 'block', 'textAlign': 'center'}),
        html.Div([
            # dcc.Input(id='search_input', type='text',
            #           placeholder='Search for the name of the player you want to substitute', debounce=False),
            dcc.Dropdown(playerNames, id='select_player_name', placeholder="Search for a player..."),
            html.Div(id='little_search_icon',
                     style={'backgroundSize': 'cover',
                            'background-image': 'url(' + dash.get_asset_url('icons/icons8-search-60.png') + ')'})
        ], id='search_input_container'),
        html.Div([], id='results')
    ], id='search_box'),
]
