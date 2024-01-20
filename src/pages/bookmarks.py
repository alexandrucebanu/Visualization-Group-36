import dash
from dash import html
from pages.components.header import getAppHeader
from dash import callback
from dash import Input, Output
from dash import dcc
import plotly.graph_objects as go
from .helper_functions import import_data

dash.register_page(__name__, path_template='/bookmarks')

sourceDF = import_data.importData()

chosen_players = [456, 362, 22]

def layout():
    return html.Div(id='bookmarks_page', children=[
        dcc.Store('chosen_player', storage_type='local'),
        getAppHeader(),
        
        html.Section([

            html.Aside(id='aside', children=[
                html.Div(className='placeholder', children='Chosen Player Box'),
                html.Div(className='placeholder', children='Bookmarked Players'),
            ]),

            addTabs(),
            
        ])

    ])


def addTabs():
    return html.Div([
    dcc.Tabs(
        id="tabs-with-classes",
        value='tab-shooting',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='Statistics',
                value='tab-stats',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Passing',
                value='tab-passing',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Set Piece',
                value='tab-set-piece', className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='GCA',
                value='tab-gca',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Shooting',
                value='tab-shooting',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Defense',
                value='tab-defense',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
        ]),
    html.Div(id='tabs-content-classes')
    ])

@callback(Output('tabs-content-classes', 'children'),
              Input('tabs-with-classes', 'value'))
def render_content(tab):
    if tab == 'tab-stats':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-passing':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-set-piece':
        return html.Div([
            html.H3('Tab content 3')
        ])
    elif tab == 'tab-gca':
        return html.Div([
            html.H3('Tab content 4')
        ])
    elif tab == 'tab-shooting':
        
        categories = ['shots_per90','shots_on_target_per90','goals_per_shot_on_target',
              'average_shot_distance', 'shots_free_kicks', 'pens_made']

        fig = go.Figure()

        for player_ID in chosen_players:
            
            fig.add_trace(go.Scatterpolar(
                theta=categories,
                r=[sourceDF[var] for var in categories],
                fill='toself',
                name='Product A'
            ))
        
        fig.update_layout(
        polar=dict(
            radialaxis=dict(
            visible=True,
            #range=[0, 5]
            )),
        showlegend=False
        )

        fig.update_layout(showlegend=True)
        fig.update_layout(margin={'l': 400, 't': 40, 'b': 0, 'r': 0})
        
        return html.Div([
            dcc.Graph(figure=fig, config={'staticPlot': True})
        ])
    elif tab == 'tab-defense':
        return html.Div([
            html.H3('Tab content 6')
        ])