import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os
import plotly.express as px


# General plots content
def general_plots_component(player=None): 
    return         html.Div(id='rectangle_general_plots',
            children=[html.Div(id='position_container_general', style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}, children=[html.H3(id='title_general_plots', children="General plots", style={'color': '#243E4C', 'margin': '0', 'marginRight': '10px'}), ]), html.Br(),
                
                html.Div(id='graph_inside_rectangle_general', 
                    children=[dcc.Graph(id='graph1_general', 
                        figure={}, 
                        style={"borderBottom": "1px dashed #ededed"})]), 
                    
                html.Br(), html.Div(id='graph_inside_rectangle2_general', 
                    children=[dcc.Graph(id='graph2_general', 
                        figure={}, style={"borderRadius": "15px"})])
                ]) 