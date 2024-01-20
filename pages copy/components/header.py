import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

def getAppHeader():
    return html.Header([html.Img(id='header_logo', src=dash.get_asset_url('logo.png')), 
    
        html.Button(html.Img(id='bookmarked_checkout', 
            src=dash.get_asset_url('icons/shopping_cart_checkout.svg')), 
            id='checkout', 
            n_clicks=0,
            style={'float': 'right'}),

        html.Div(id='box_container', 
                    children=[
                        html.Div(id='rectangle')],
                        style={'display': 'none'}) 
    ])