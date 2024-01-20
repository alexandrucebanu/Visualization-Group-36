import dash
from dash import html
from pages.components.header import getAppHeader
from dash import callback
from dash import Input, Output
from dash import dcc
from .player_chosen import sourceDF, getPlayerImageElement
from .helper_functions import import_data

dash.register_page(__name__, path_template='/bookmarks')

# Import Data, make Dataframe
sourceDF = import_data.importData()

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
                    radar_chart(df_data),
                ])
            ])
        ])
    ])

# General plots content
def radar_chart(): 
    return  html.Div(id='radar_chart',
            children=[html.Div(id='container', 
                style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}, 
                children=[html.H3(id='title_radar', 
                    children="Radar Chart", style={'color': '#243E4C', 'margin': '0', 'marginRight': '10px'}), ]), 
            html.Br(),
            html.Div(id='graph_inside_rectangle_general', 
                children=[dcc.Graph(id='radar_graph', figure={}, style={"borderBottom": "1px dashed #ededed"})]), 
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

# -------------------------------------------------------------
# Callbacks radar plot
# -------------------------------------------------------------
@callback(
        Output(component_id='radar_graph', component_property='figure'),)
def update_general_plots(filters):

    # TODO: Change the parameters of the plots!
    try:
        theta = []
        fig = px.line_polar(sourceDF, r='r', theta='theta', line_close=True)

        # fig12 = px.scatter(filterDataFrame, x="movement_sprint_speed", y='power_stamina', title='Sprint Speed and Stamina', labels={'movement_sprint_speed': 'Sprint Speed [FIFA scores]', 'power_stamina': 'Stamina [FIFA scores]'}, hover_data=['player'])
        # fig22 = px.scatter(filterDataFrame, x="power_jumping", y='movement_reactions', title='Power Jumping and Movement Reaction', labels={'power_jumping': 'Power Jumping [FIFA Scores]', 'movement_reactions': 'Movement Reactions [FIFA Scores]'}, hover_data=['player'])

        return fig

    except:
        return dash.no_update
