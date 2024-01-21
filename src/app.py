# General Imports
import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

app.layout = html.Div([dash.page_container], id='app_container')

app.run(debug=True, port=2030, dev_tools_hot_reload=False, dev_tools_hot_reload_interval=100)