import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os
import plotly.express as px

# Data
# --------------------------------------------------------------------------------------------------------------
df_possession = pd.read_csv("/Users/alexandrucebanu/Desktop/BACHELOR/YEAR 2/Q2/JBI100 Visualization/Visualization's dashboard/notebooks/data/player_possession.csv")

# App layout
# --------------------------------------------------------------------------------------------------------------

specific_plots_component = html.Div([
    html.H1('Player specific graphs', style={'color': '#243E4C', 'textAlign': 'center'}),
    html.Br(),
    html.Div(id='rectangle_specific_plots',
             children=[
                 html.Div(id='position_and_dropdown_container',
                          style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
                          children=[
                              html.H3("Position:", style={'color': '#243E4C', 'margin': '0', 'marginRight': '10px'}),
                              dcc.Dropdown(id='dropdown', options=[
                                  {'label': 'Forward', 'value': 'FW'},
                                  {'label': 'Middle', 'value': 'MID'},
                                  {'label': 'Back', 'value': 'BK'},
                                  {'label': 'Goalkeeper', 'value': 'GK'}
                              ], value='FW', style={'width': '300px'})  # Adjust the width as needed
                          ]),
                 # html.Div(id='output_container', children=[]),
                 html.Br(),
                 html.Div(id='graph_inside_rectangle',
                          children=[
                              dcc.Graph(id='graph1', figure={}, style={
                                  "box-shadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)",
                                  "borderRadius": "15px"})
                          ]),
                 html.Br(),
                 html.Div(id='graph_inside_rectangle2',
                          children=[
                              dcc.Graph(id='graph2', figure={}, style={
                                  "box-shadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)",
                                  "borderRadius": "15px"})
                          ])
             ])
])
# ----------------------------------------------------------------------------------------------------------------------

# Callback
# --------------------------------------------------------------------------------------------------------------

@callback(
    [Output(component_id='graph1', component_property='figure'),
     Output(component_id='graph2', component_property='figure')],
    [Input(component_id='dropdown', component_property='value')]
)
def update_output(position):
    # container = "You have chosen the position: {}".format(position)

    filtered_df = df_possession[df_possession['position'] == position]

    fig1 = px.scatter(filtered_df, x='dribbles_completed', y='miscontrols')
    fig2 = px.bar(filtered_df, x='dispossessed', y='miscontrols')

    return fig1, fig2

# ----------------------------------------------------------------------------------------------------------------------

