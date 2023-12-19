
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import os

import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os

filePath = os.path.join(os.path.dirname(__file__), '../../data/players_22.csv')
df_general = pd.read_csv(filePath)


# Speed over power
speed_power_jump = html.Div(id='speed_power_jump',children=[

    html.H3('Speed vs. Power Jump',  style={'textAlign': 'center'} ),
    dcc.Graph(id="scatter-plot", style={'width': '50vh', 'height': '50vh', 'align': 'center'}),
    
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
        df_general[mask], x="movement_sprint_speed", y="movement_acceleration",
        hover_data=['long_name'])
    return fig




# OTHER Plot
speed_power_jump2 = html.Div(id='speed_power_jump2',children=[

    html.H3('Atacking vs. Defending',  style={'textAlign': 'center'} ),
    dcc.Graph(id="scatter-plot2", style={'width': '50vh', 'height': '50vh', 'align': 'center'}),
    
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
        df_general[mask], x="power_strength", y="power_stamina",
        hover_data=['long_name'])
    return fig2

