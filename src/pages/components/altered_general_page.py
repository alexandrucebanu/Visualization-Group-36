import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os
import plotly.express as px

# The following dictionary will be used to map positions from dataset to human-readable titles
positionForHumanDictionary = {'FW': 'Forward', 'GK': 'Goalkeeper', 'MF': 'Middle Field', 'DF': 'Defender'}



def getHumanReadableFeatureName(featureName):
    mapping = {
        'gca': 'goal creating actions',
        'sca': 'Shot Creating Actions',
        'goals_pens': 'Non-Penalty Goals',
        'progressive_passes_received': 'Progressive Passes Received',
        'touches_att_pen_area': 'Touches in Attacking Penalty Area',
        'assists_per90': 'Assists per 90 minutes',
        'goals_per90': 'Goals per 90 minutes'
    }
    if featureName in mapping.keys():
        featureName = mapping[featureName]
    return featureName.replace('_', ' ').title()



# App layout
# --------------------------------------------------------------------------------------------------------------


def featureNamesTransformed(name):
    mapping = {
        'gca': 'goal creating actions',
        'sca': 'Shot Creating Actions',
        'goals_pens': 'Non-Penalty Goals',
        'progressive_passes_received': 'Progressive Passes Received',
        'touches_att_pen_area': 'Touches in Attacking Penalty Area',
        'assists_per90': 'Assists per 90 minutes',
        'goals_per90': 'Goals per 90 minutes'
    }
    if name in list(mapping.keys()):
        return mapping[name]
    return name


def main_page_changed(player=None, colorMap=None):
    position = player['position']
    positionAttributes = {
        'FW': ['shots_on_target', 'goals', 'dribbles_completed', 'miscontrols', 'goals_pens', 'assists_per90', 'sca', 'progressive_passes_received', 'goals_per90', 'touches_att_pen_area'],
        'MF': ['gca', 'passes_completed', 'dribbles_completed', 'miscontrols', 'touches_att_pen_area', 'assists_per90', 'goals_per90', 'assists'],
        'DF': ['blocked_passes', 'clearances', 'tackles_won', 'interceptions', 'tackles', 'crosses', 'passes_completed', 'tackles_interceptions', 'fouls'],
        'GK': ['gk_save_pct', 'gk_goals_against_per90', 'gk_clean_sheets', 'age', 'gk_crosses_stopped', 'gk_wins', 'gk_losses', 'gk_pens_saved', 'gk_pens_allowed']
    }
    defaultSelectedAttributes = {
        'FW': ['shots_on_target', 'goals', 'dribbles_completed', 'miscontrols'],
        'MF': ['gca', 'passes_completed', 'dribbles_completed', 'miscontrols'],
        'DF': ['blocked_passes', 'clearances', 'tackles_won', 'interceptions'],
        'GK': ['gk_save_pct', 'gk_goals_against_per90', 'gk_clean_sheets', 'age']
    }

    return html.Div([
        html.Div(id='second_half',
            children=[
                html.H3(id='position', children="Position: {}".format(positionForHumanDictionary[player['position']]), style={'color': '#243E4C', "marginTop": "20px"}),

                html.Div([
                    html.Div(id='position_container_general',
                        style={'alignItems': 'center', 'justifyContent': 'center'}),
                    html.Div(id='graph_inside_rectangle_general',
                        children=[
                            dcc.Graph(id='graph1_general', figure={}),
                            dcc.Graph(id='graph2_general', figure={})
                        ]),
                    html.Div(id='plot_legends', children=[
                        html.Div(className='legend-color', children=[html.Div(style={'background': colorMap['chosen']}),
                                                                     html.Span('Player to replace')]),
                        html.Div(className='legend-color',
                                 children=[html.Div(style={'background': colorMap['bookmarked']}),
                                           html.Span('Bookmarked players')]),
                        html.Div(className='legend-color',
                                 children=[html.Div(style={'background': colorMap['candidate']}),
                                           html.Span('Current candidate')]),
                        html.Div(className='legend-color',
                                 children=[html.Div(style={'background': colorMap['others']}), html.Span('Others')]),
                    ]),
                ], style={'overflow': 'hidden'})
            ]),
        html.Div(id='first_half',

            children=[
                html.Div(id='position_container',
                    style={'alignItems': 'center', 'justifyContent': 'center'},
                    children=[
                        html.Div(className='chose_attributes', children=[
                            html.Label('Attributes to compare:', className='chose_attributes_label'),
                            dcc.Dropdown(id="attributes_dropdown",
                                options=[{'label': getHumanReadableFeatureName(option), 'value': option} for option in positionAttributes[position]],
                                value=defaultSelectedAttributes[position], multi=True, style={"float": 'left', "width": "calc(100% - 150px)", "padding": "0 2px"})
                        ]), ]),

                html.Div(id='graph_inside_rectangle', children=[dcc.Graph(id='graph1', figure={}, style={
                    "borderBottom": "1px dashed #ededed"}
                )])]
        ),
    ])