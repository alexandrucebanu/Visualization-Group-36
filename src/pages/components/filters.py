import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
from ..helpers import fontIcon
#from dataAdapters import getMergedDataFrame
import plotly.express as px


def layout(sourceDF,chosenPlayer):
    possiblePositions = list(sourceDF['position'].unique())  # TODO: this might not be very efficient (it's a static list but it's computed by every render)
    a = sourceDF['age']
    nrbins = len(a.unique())
    fig = px.histogram(sourceDF, x="age", nbins=nrbins)
    fig.update_traces(marker_color='#2196f3')
    fig.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False)
    fig.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')
    return html.Div([html.Div([html.H3("Filters", className="block_title"), html.Div(
        [html.H3('Filter based on age'), html.Div("Waiting...", id='age_histogram'), dcc.RangeSlider(min(a), max(a), value=[min(a), max(a)], tooltip={"placement": "bottom", "always_visible": True}, id='age_slider', step=1, marks={min(a) + 3 * int(i / 3): str(min(a) + 3 * int(i / 3)) for i in range(round((max(a) - min(a)) * 3))}), ],
        id='wage_filter', className='filter_block'), html.Div([html.H3('Filter based on position'), html.Div([

        dcc.Checklist(['GK','DF','MF','FW'], [chosenPlayer['position']],id='chosen_positions')], id='map_filter', style={'backgroundImage': 'url({})'.format(dash.get_asset_url('backgrounds/field.png'))})], className='filter_block')], className="filters_block")])
