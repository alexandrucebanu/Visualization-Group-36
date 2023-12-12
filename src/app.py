## General Imports
import dash
import numpy as np
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import os

## TODO: generate a catch for when the data directory does not exist

filePath = os.path.join(os.path.dirname(__file__), 'data/player_gca.csv')
df_defense = pd.read_csv(filePath)
playerNames = np.array(df_defense.player, dtype=str)

# TODO: sort based on how early the search word appears in the string
# TODO: make the search functionality case-insensitive
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div(id='logo',
                 style={'background': 'url(' + dash.get_asset_url('icons/icons8-soccer-94.png') + ')'}),

        html.H1('Welcome to Stratinder', style={'color': '#243E4C', 'display': 'block', 'textAlign': 'center'}),
        html.Div([
            dcc.Input(id='search_input', type='text',
                      placeholder='Search for the name of the player you want to substitute', debounce=False),
            html.Div(id='little_search_icon',
                     style={'backgroundSize': 'cover',
                            'background-image': 'url(' + dash.get_asset_url('icons/icons8-search-60.png') + ')'})
        ], id='search_input_container'),
        html.Div([], id='results')
    ], id='search_box'),
])


@callback(
    Output('results', 'children'),
    Input('search_input', 'value')
)
def updateSearch(value):
    if (value == None):
        return ''
    mask = np.char.find(playerNames, value) != -1
    resultList = [html.Div(name, className='search_result') for name in playerNames[mask]]
    if (len(resultList) == 0):
        return [html.Div('Nothing found!')]
    return resultList


app.run(debug=True)
