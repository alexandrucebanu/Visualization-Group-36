import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table

dash.register_page(__name__)
layout = [
    html.Div('Hi and welcome'),
]
