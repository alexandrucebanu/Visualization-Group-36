import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os
import plotly.express as px

# The following dictionary will be used to map positions from dataset to human-readable titles
positionForHumanDictionary = {'FW': 'Forward', 'GK': 'Goalkeeper', 'MF': 'Middle Field', 'DF': 'Defender'}


# App layout
# --------------------------------------------------------------------------------------------------------------

def specific_plots_component(player=None):
    return html.Div([dcc.Location(id='url', refresh=False), html.Div(id="page", style={'display': 'flex'}, children=[

        html.Div(id='rectangle_specific_plots',
            children=[html.Div(id='position_container', style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}, children=[html.H3(id='position', children="Position: {}".format(positionForHumanDictionary[player['position']]), style={'color': '#243E4C', 'margin': '0', 'marginRight': '10px'}), ]), html.Br(),
                html.Div(id='graph_inside_rectangle', children=[dcc.Graph(id='graph1', figure={}, style={

                    "borderBottom": "1px dashed #ededed"})]), html.Br(), html.Div(id='graph_inside_rectangle2', children=[dcc.Graph(id='graph2', figure={}, style={

                    "borderRadius": "15px"})])])])])
