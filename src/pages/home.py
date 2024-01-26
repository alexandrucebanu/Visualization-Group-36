import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os
from . import helpers
from urllib.parse import quote

dash.register_page(__name__, path='/')

# TODO: team data placement instruction in README.md <- We're using `group_stats.csv` right now
# TODO: generate a catch for when the data directory does not exist

filePath = os.path.join(os.path.dirname(__file__), '../data/merged_data.csv')
sourceDF = pd.read_csv(filePath)
playersList = [(index, player['player']) for index, player in sourceDF.iterrows()]

layout = [
    html.Div([
        # Header with a background image
        dcc.Store('chosen_player',storage_type='local'),
        dcc.Store('chosen_player_id',storage_type='local'),
        html.Div(id='search_box_header', style={'background': (
            'linear-gradient(rgba(255,255,255,0), rgba(0,0,0,0.65)), url({}) center'.format(
                dash.get_asset_url('backgrounds/soccer_field.jpg')))}),
        # Logo image
        html.Div(id='logo',
                 style={'background': 'url(' + dash.get_asset_url('icons/icons8-soccer-94.png') + ')'}),

        html.H1('Welcome to Stratinder', style={'color': '#243E4C', 'display': 'block', 'textAlign': 'center'}),
        # Search input container
        html.Div([
            # dcc.Input(id='search_input', type='text',
            #           placeholder='Search for the name of the player you want to substitute', debounce=False),
            dcc.Dropdown(options=[{'label': playerItem[1], 'value': playerItem[0]} for playerItem in playersList],
                         id='select_player_name', placeholder="Search for a player..."),
            html.Div([], id='results'),
            html.Div(id='little_search_icon',
                     style={'backgroundSize': 'cover',
                            'background-image': 'url(' + dash.get_asset_url('icons/icons8-search-60.png') + ')'})
        ], id='search_input_container'),
        html.Div([], id='results')
    ], id='search_box'),
]

# Callback function for updating search results based on player selection
@callback(Output('chosen_player_id','data'),Output('chosen_player','data'),Output('results', 'children'), Input('select_player_name', 'value'))
def choosePlayer(playerIdValue=None):
    """
    Updates the results section with player information based on the selected player ID.
    If no player is selected, it returns an empty string.
    """
    if not playerIdValue:
        return None,None,""
    playerRow = sourceDF.iloc[[playerIdValue]].to_dict(orient='records')[0]
    return (int(playerIdValue),playerRow,[
        html.A([helpers.fontIcon('chevron_right'), "Explore replacements for {}".format(playerRow['player'])],
               href='/replace/{}'.format(playerIdValue),
               id="go_to_player_page")
    ])