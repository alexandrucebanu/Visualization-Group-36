import dash
from dash import html

def getAppHeader():
    return html.Header([html.Img(id='header_logo', src=dash.get_asset_url('logo.png')), ])
