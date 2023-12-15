from dash import html, dcc
from ..helpers import fontIcon
from dataAdapters import getMergedDataFrame
import plotly.express as px


def layout():
    df = getMergedDataFrame()
    df

    def getAgeYears(ageString):
        return int(ageString.split('-')[0])

    df['age'] = (df['age']).map(getAgeYears)
    fig = px.histogram(df, x="age",)

    return [
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
                dcc.RangeSlider(0, 20, marks=None, value=[5, 15]),
                dcc.Graph(figure=fig)

            ], id='wage_filter'),
        ], className="filters_block")
    ]
