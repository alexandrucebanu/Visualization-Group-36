import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os
import plotly.express as px


# Third try
def general_plots_component(player=None): 
    return         html.Div(id='rectangle_general_plots',
            children=[html.Div(id='position_container_general', style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}, children=[html.H3(id='title_general_plots', children="General plots", style={'color': '#243E4C', 'margin': '0', 'marginRight': '10px'}), ]), html.Br(),
                html.Div(id='graph_inside_rectangle_general', children=[dcc.Graph(id='graph1_general', figure={}, style={

                    "borderBottom": "1px dashed #ededed"})]), html.Br(), html.Div(id='graph_inside_rectangle2_general', children=[dcc.Graph(id='graph2_general', figure={}, style={

                    "borderRadius": "15px"})])])












# Second try
def general_plots_component2(player=None):
    return html.Div([dcc.Location(id='url2', refresh=False), html.Div(id="page2", style={'display': 'flex'}, children=[

        html.Div(id='rectangle_specific_plots2',
            children=[html.Div(id='position_container2', style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}, children=[html.H3(id='position2', children="Title", style={'color': '#243E4C', 'margin': '0', 'marginRight': '10px'}), ]), html.Br(),
                html.Div(id='graph_inside_rectangle2', children=[dcc.Graph(id='graph12', figure={}, style={

                    "borderBottom": "1px dashed #ededed"})]), html.Br(), html.Div(id='graph_inside_rectangle22', children=[dcc.Graph(id='graph22', figure={}, style={

                    "borderRadius": "15px"})])])])])



# Inspired by Alexandru's code
def general_plots_component_():

    return html.Div([dcc.Location(id='url2', refresh=False), html.Div(id="page2", style={'display': 'flex'}, children=[

        html.Div(id='rectangle_specific_plots2',
            children=[html.Div(id='position_container2', style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}, children=[
                        html.H3(id='position2', children="General Plots", style={'color': '#243E4C', 'margin': '0', 'marginRight': '10px'}), ]), html.Br(),
                
                html.Div(id='graph_inside_rectangle2', children=[dcc.Graph(id='graph12', figure={}, style={

                    "borderBottom": "1px dashed #ededed"})]), html.Br(), html.Div(id='graph_inside_rectangle22', children=[dcc.Graph(id='graph22', figure={}, style={

                    "borderRadius": "15px"})])])])])
























"""

filePath = os.path.join(os.path.dirname(__file__), '../../data/players_22.csv')
df_general = pd.read_csv(filePath)



# Speed Plot
speed_power_jump = html.Div(id='speed_power_jump',children=[

    html.H3('Speed vs. Power Jump',  style={'textAlign': 'center'} ),
    dcc.Graph(id="scatter-plot", style={'width': '100%', 'height': '100%', 'align': 'center'}),
    
    html.P("Filter by sprint speed:"),
    dcc.RangeSlider(
        id='range-slider',
        min=0, max=100, step=0.1,
        marks= {num: str(num) for num in range(0,100,10)},
        value=[0, 100],
    ),
])

@callback(
    Output("scatter-plot", "figure"), 
    Input("range-slider", "value"))

def update_bar_chart(slider_range):
    low, high = slider_range
    mask = (df_general['movement_agility'] > low) & (df_general['movement_agility'] < high)
    fig = px.scatter(
        df_general[mask], x=(df_general[mask]["height_cm"]*df_general[mask]['weight_kg']), y="movement_agility",
        hover_data=['long_name'])
    return fig


# Power Plot
speed_power_jump2 = html.Div(id='speed_power_jump2',children=[

    html.H3('Atacking vs. Defending',  style={'textAlign': 'center'} ),
    dcc.Graph(id="scatter-plot2", style={'width': '100%', 'height': '100%', 'align': 'center'}),
    
    html.P("Filter by movement agility:"),
    dcc.RangeSlider(
        id='range-slider2',
        min=0, max=100, step=0.1,
        marks= {num: str(num) for num in range(0,100,10)},
        value=[0, 100],
    ),
])

@callback(
    Output("scatter-plot2", "figure"), 
    Input("range-slider2", "value"))

def update_bar_chart(slider_range):
    low, high = slider_range
    mask = (df_general['power_jumping'] > low) & (df_general['power_jumping'] < high)
    fig2 = px.scatter(
        df_general[mask], x=(df_general[mask]["movement_acceleration"]*df_general[mask]['movement_sprint_speed']*df_general[mask]["movement_agility"]), 
        y='power_stamina',
        hover_data=['long_name'])
    return fig2"""