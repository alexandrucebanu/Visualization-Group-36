from dash import Dash, html, dcc, callback, Output, Input, dash_table
from ..helpers import fontIcon
from dataAdapters import getMergedDataFrame
import plotly.express as px


def getAgeYears(ageString):
    return int(ageString.split('-')[0])


def layout():
    df = getMergedDataFrame()
    df

    df['age'] = (df['age']).map(getAgeYears)
    a = df['age']
    nrbins = len(a.unique())
    fig = px.histogram(df, x="age", nbins=nrbins)
    fig.update_traces(marker_color='#2196f3')
    fig.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False)
    fig.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')
    return html.Div([
        html.Div([
            html.H3("Filters", className="block_title"),
            html.Div([
                html.Div([
                    fontIcon('tune'),
                    'Filters'
                ], className='tab_switch_option active'),
                html.Div([
                    fontIcon('bookmark'),
                    'Bookmarks'
                ], className='tab_switch_option'),
            ], className='tab_switch'),
            html.Div([
                html.H3('Filter based on age'),
                html.Div("Waiting...", id='age_histogram'),
                dcc.RangeSlider(min(a), max(a), value=[min(a), max(a)],
                                tooltip={"placement": "bottom", "always_visible": True},
                                id='age_slider',
                                step=1,
                                marks={min(a) + 3 * int(i / 3): str(min(a) + 3 * int(i / 3)) for i in
                                       range(round((max(a) - min(a)) * 3))}
                                ),

            ], id='wage_filter', className='filter_block'),
        ], className="filters_block")
    ])


@callback(Output('age_histogram', 'children'), Input('age_slider', 'value'))
def apply_age_filter(value):
    df = getMergedDataFrame()
    df['age'] = (df['age']).map(getAgeYears)
    a = df['age']
    mask = ((a >= value[0]) & (a <= value[1]))

    def map_in_bound(value):
        if (value):
            return "YES"
        return "NO"

    df['in_bound'] = mask.map(map_in_bound)

    nrbins = len(a.unique())
    fig = px.histogram(df, x="age", nbins=nrbins, color='in_bound',
                       color_discrete_map={"YES": "#2196f3", "NO": "#E9E9E9"})
    fig.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False,
                      showlegend=False)
    fig.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')
    return dcc.Graph(figure=fig, config={'staticPlot': True},
                     style={'width': 'calc(100% - 20px)', 'height': '60px', 'margin': '5px auto'}),

    return "OK the values are {} and {}".format(value[0], value[1])
