# General Imports
import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table



app = Dash(__name__, use_pages=True)
#
app.layout = html.Div([dash.page_container], id='app_container')

app.run(debug=False, port=2030)



