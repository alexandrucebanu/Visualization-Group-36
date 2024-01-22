import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
from ..helpers import fontIcon

from dataAdapters import getMergedDataFrame
import plotly.express as px


def layout(sourceDF,chosenPlayer):
    possiblePositions = list(sourceDF['position'].unique())  # TODO: this might not be very efficient (it's a static list but it's computed by every render)
    ageSeries = sourceDF['age']
    wageSeries = sourceDF['wage_eur']
    nrbins = len(ageSeries.unique())
    nrbinsWage = len(wageSeries.unique())
    fig = px.histogram(sourceDF, x="age", nbins=nrbins)
    fig.update_traces(marker_color='#2196f3')
    fig.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False)
    fig.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')
    return html.Div([html.Div([
        html.H3("Filters", className="block_title"), 
        
        # Age / Wage filter
        html.Div(
            [html.H3('Filter based on age'), 
            html.Div("Waiting...", id='age_histogram'), 
            dcc.RangeSlider(min(ageSeries), max(ageSeries), value=[min(ageSeries), max(ageSeries)],
                tooltip={"placement": "bottom", "always_visible": True}, 
                id='age_slider', step=1, marks={min(ageSeries) + 3 * int(i / 3): str(min(ageSeries) + 3 * int(i / 3)) for i in range(round((max(ageSeries) - min(ageSeries)) * 3))})],
            id='age_filter', className='filter_block'),
        html.Div(
            [html.H3('Filter based on wage'),
            html.Div("Waiting...", id='wage_histogram'),
            dcc.RangeSlider(min(wageSeries), max(wageSeries), value=[min(wageSeries), max(wageSeries)],
                tooltip={"placement": "bottom", "always_visible": True},
                id='wage_slider', step=50000)],
            id='wage_filter', className='filter_block'),

        # Position filter
        html.Div(
            [html.H3('Filter based on position'), html.Div([
            dcc.Checklist(['GK','DF','MF','FW'], 
                [chosenPlayer['position']],
                id='chosen_positions')], 
            id='map_filter', className='filter_block', style={'backgroundImage': 'url({})'.format(dash.get_asset_url('backgrounds/field.png'))})]), 
        

        # Filter based on foot preference
        html.Div(
            [html.H3('Filter based on dominant foot'), html.Div([
            dcc.Checklist(['Left','Right'], 
                ['Left','Right'],
                id='foot_preference')],
            id='foot_filter', className='filter_block', style={'backgroundImage': 'url({})'.format(dash.get_asset_url('icons/football_shoes.png'))})]), 
            # map_filter has something to do with the image appearing..... change id to foot_filter

        ])],

        className="filters_block")
