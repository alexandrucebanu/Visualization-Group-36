import dash
from dash import html
from pages.components.header import getAppHeader
from dash import callback
from dash import Input, Output
from dash import dcc
from .player_chosen import sourceDF, getPlayerImageElement

dash.register_page(__name__, path_template='/bookmarks')



def layout(player_id=None):
    # player = sourceDF.iloc[[player_id]].to_dict(orient='records')[0]
    return html.Div(id='bookmarks_page', children=[
        dcc.Store('chosen_player', storage_type='local'),
        getAppHeader(),
        html.Section([

            html.Aside(id='aside', children=[
                html.Div(id='chosen_player_box', className='player-info-box', children=[
                    'HIIII'
                ]),

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



@callback(Output('chosen_player_box', 'children'), Input('chosen_player', 'data'))
def updateFirstPlaceHolder(chosenPlayer):
    print(chosenPlayer)
    return [
                    html.Img(src='assets/icons/player.png', className='player-image'),
                    html.Div(className='player-details',style={'borderLeft':'1px solid #ededed','paddingLeft':'12px'}, children=[
                        html.H4(chosenPlayer['player'], className='chosen_player_name'),
                        html.Div(className='separating-bar'),
                        html.P('AGE: {}'.format(chosenPlayer['age']), className='chosen_player_age'),
                        html.P('HEIGHT: {}'.format(chosenPlayer['height_cm']), className='chosen_player_height'),
                        html.P('FOULS: {}'.format(chosenPlayer['fouls']), className='chosen_player_fouls'),
                        html.P('CARDS: yellow: {}, red: {}, yellow2: {}'.format(chosenPlayer['cards_yellow'], chosenPlayer['cards_red'], chosenPlayer['cards_yellow_red']), className='chosen_player_cards'),
                    ])
                ]
