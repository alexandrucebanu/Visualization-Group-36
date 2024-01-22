import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State


def getAppHeader():
    return html.Header([html.Img(id='header_logo', src=dash.get_asset_url('logo.png')),

        html.Button(id='checkout', children=[html.Span(id='bookmarks_count'), html.Span(className='material-symbols-rounded', children='shopping_cart')]),

        html.Div(id='bookmarks_sidebar_back', style={'display': 'none'}),
        html.Div(id='bookmarks_sidebar', style={'display': 'none'},
            children=[
                html.Div([
                    html.H3('Bookmarked Player'),
                    html.Button(id='clear_bookmarks', children='Clear all'),
                ], style={'overflow': 'hidden'}),
                html.Div(id='bookmarks_sidebar_list'),
                dcc.Link(children=[
                    html.Span(className='icon', style={'background-image': 'url({})'.format(dash.get_asset_url('icons/check.png'))}),
                    'Compare bookmarks'
                ], href='/bookmarks', id='compare_bookmarks')
            ]),

    ])
