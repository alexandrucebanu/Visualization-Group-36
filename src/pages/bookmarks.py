import dash
from dash import html
from pages.components.header import getAppHeader
from dash import callback
from dash import Input, Output
from dash import dcc

dash.register_page(__name__, path_template='/bookmarks')



def layout():
    return html.Div(id='bookmarks_page', children=[
        dcc.Store('chosen_player', storage_type='local'),
        getAppHeader(),
        html.Section([

            html.Aside(id='aside', children=[
                html.Div(className='placeholder', children='Chosen Player Box'),
                html.Div(className='placeholder', children='Bookmarked Players'),
            ]),

            html.Div(id='columns', children=[
                html.H3('Comparison of bookmarked players', id='bookmarked_players_view_title'),
                html.Div(id='bookmarked_view_plots', children=[
                    html.Div(id='first_placeholder', className='placeholder', children='Plot placeholder'),
                    html.Div(className='placeholder', children='Plot placeholder'),
                    html.Div(className='placeholder', children='Plot placeholder'),
                    html.Div(className='placeholder', children='Plot placeholder'),
                ])
            ])
        ])

    ])




# The following is only a dummy code for other members to have a template of how they can access chosen player information.
# It displays the name of the chosen player in the first block on the right-side. Feel free to delete it later.
# Go make so:wqmething great! 😀
@callback(Output('first_placeholder', 'children'), Input('chosen_player', 'data'))
def updateFirstPlaceHolder(chosenPlayer):
    return "Chosen player is : {}".format(chosenPlayer['player'])
