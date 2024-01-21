import dash
from dash import html
from pages.components.header import getAppHeader
from dash import callback
from dash import Input, Output
from dash import dcc
import plotly.graph_objects as go
from .helper_functions import import_data
from sklearn.preprocessing import StandardScaler
import pandas as pd
from .helper_functions import import_data

# from .player_chosen import sourceDF, getPlayerImageElement
sourceDF = import_data.importData()

dash.register_page(__name__, path_template='/bookmarks')

# Dummy players
# chosen_players = [482, 388, 134] # Neymar, messi, Ronaldo
chosen_players = [4, 83, 410]  # Neymar, messi, Ronaldo

sourceDF = import_data.importData()
df_standardised = pd.DataFrame()

# Statistics categories
categories_stats = ['games', 'minutes_90s', 'cards_red', 'cards_yellow']
titles_stats = ['Number of games', 'Minutes Player / 90', 'Red Cards', 'Yellow Cards']

# Passing categories
categories_passing = ['passes_pct', 'passes_progressive_distance', 'passes_pct_short', 'passes_pct_medium', 'passes_pct_long']
titles_passing = ['Percentage Completed Passes', 'Total Progressive Distance', 'Percentage of Completed Short-Distance Passes', 'Percentage of Completed Medium-Distance Passes', 'Percentage of Completed Long-Distance Passes']

# Set Piece
categories_set_piece = ['throw_ins', 'corner_kicks_in', 'corner_kicks_out', 'corner_kicks_straight', 'corner_kicks']
titles_set_piece = ['Number of Throw-Ins', 'Number of Corner Kicks', 'Number of Corner Kicks type "In"', 'Number of Corner Kicks type "Out"', 'Number of Corner Kicks type "Straight"']

# GCA categories
categories_gca = ['sca', 'sca_per90', 'gca', 'gca_per90']
titles_gca = ['Shot-Creating Actions', 'Shot-Creating Actions per 90 min', 'Goal-Creating Actions', 'Goal-Creating Actions per 90 min']

# Shooting categories
categories_shooting = ['shots_per90', 'shots_on_target_per90', 'goals_per_shot_on_target',
    'average_shot_distance', 'shots_free_kicks', 'pens_made']
titles_shooting = ['Shots per 90', 'Shots on Target per 90', 'Goals per Shot on Target',
    'Average Shot Distance', 'Shots Free Kicks', 'Penalties made']

# Defense categories
categories_defense = ['tackles', 'tackles_won', 'dribble_tackles_pct', 'blocked_shots', 'blocked_passes']
titles_defense = ['Number of Tackles', 'Number of Tackles Won', 'Percentage of Tackles which are type "Dribble"', 'Percentage of Tackles which are type "Shots"', 'Percentage of Tackles which are type "Passes"']

categories = categories_stats + categories_passing + categories_set_piece + categories_gca + categories_shooting + categories_defense
titles = titles_stats + titles_passing + titles_set_piece + titles_gca + titles_shooting + titles_defense

for col in categories:
    df_standardised[col] = (sourceDF[col] - sourceDF[col].mean()) / sourceDF[col].std()

df_standardised.rename(columns={categories[i]: titles[i] for i in range(len(categories))}, inplace=True)

min_vals = df_standardised.min()
df_standardised[titles] = df_standardised[titles] - min_vals


def layout(player_id=None):
    # player = sourceDF.iloc[[player_id]].to_dict(orient='records')[0]
    return html.Div(id='bookmarks_page', children=[
        dcc.Store('chosen_player', storage_type='local'),
        dcc.Store(id='bookmarked_players', storage_type='local', data=[]),

        getAppHeader(),

        html.Section([

            html.Aside(id='aside', children=[
                html.Div(id='chosen_player_box', className='player-info-box', children=[
                    'HIIII'
                ]),

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


def makeRadar(titles, bookmarkedPlayerIDS):
    fig = go.Figure()

    for player_ID in bookmarkedPlayerIDS:
        fig.add_trace(go.Scatterpolar(
            theta=titles,
            r=[df_standardised.loc[player_ID, var] for var in titles],
            fill='toself',
            name=sourceDF.loc[player_ID, 'player']
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showline=True,
                showticklabels=False,
                showgrid=True,
                autorange=True,
            )),
        showlegend=True
    )
    fig.update_layout(margin={'l': 400, 't': 40, 'b': 0, 'r': 0})

    return html.Div([
        dcc.Graph(figure=fig, config={'staticPlot': True})
    ])


@callback(Output('tabs-content-classes', 'children'),
    Input('tabs-with-classes', 'value'),
    Input('bookmarked_players', 'data'))
def render_content(tab, bookmarkedPlayerIDS):
    # Get list of bookmarked players
    bookmarkedPlayerIDS = list(set(bookmarkedPlayerIDS))
    bookmarkedPlayerIDS = [i for i in bookmarkedPlayerIDS if i != None]

    # Returns the appropriate radar chart
    if tab == 'tab-stats':
        return makeRadar(titles_stats, bookmarkedPlayerIDS)
    elif tab == 'tab-passing':
        return makeRadar(titles_passing, bookmarkedPlayerIDS)
    elif tab == 'tab-set-piece':
        return makeRadar(titles_set_piece, bookmarkedPlayerIDS)
    elif tab == 'tab-gca':
        return makeRadar(titles_gca, bookmarkedPlayerIDS)
    elif tab == 'tab-shooting':
        return makeRadar(titles_shooting, bookmarkedPlayerIDS)
    elif tab == 'tab-defense':
        return makeRadar(titles_defense, bookmarkedPlayerIDS)


@callback(Output('chosen_player_box', 'children'), Input('chosen_player', 'data'))
def updateFirstPlaceHolder(chosenPlayer):
    print(chosenPlayer)
    return [
        html.Img(src='assets/icons/player.png', className='player-image'),
        html.Div(className='player-details', style={'borderLeft': '1px solid #ededed', 'paddingLeft': '12px'}, children=[
            html.H4(chosenPlayer['player'], className='chosen_player_name'),
            html.Div(className='separating-bar'),
            html.P('AGE: {}'.format(chosenPlayer['age']), className='chosen_player_age'),
            html.P('HEIGHT: {}'.format(chosenPlayer['height_cm']), className='chosen_player_height'),
            html.P('FOULS: {}'.format(chosenPlayer['fouls']), className='chosen_player_fouls'),
            html.P('CARDS: yellow: {}, red: {}, yellow2: {}'.format(chosenPlayer['cards_yellow'], chosenPlayer['cards_red'], chosenPlayer['cards_yellow_red']), className='chosen_player_cards'),
        ])
    ]
