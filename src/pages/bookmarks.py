"""
This module is responsible for creating and handling the "Bookmarks" page in the dashboard.
It includes functionality for displaying and interacting with bookmarked player data.
"""

import dash
from dash import html
from dash import callback
from dash import Input, Output
from dash import dcc
import plotly.graph_objects as go
import pandas as pd
from pages.helpers import fontIcon
import os
from dataAdapters import get_first_vertical_image, playerImageDirectory, getCountryFlagPath, getPlayerTeam

# Registering this file as a Dash page with a specific URL path
dash.register_page(__name__, path_template='/bookmarks')

# Dummy players
# chosen_players = [482, 388, 134] # Neymar, messi, Ronaldo
chosen_players = [4, 83, 410]  # Neymar, messi, Ronaldo

filePath = os.path.join(os.path.dirname(__file__), ('../data/' + 'merged_data.csv'))
sourceDF = pd.read_csv(filePath)
sourceDF = sourceDF.fillna(0)

df_standardised = pd.DataFrame()

# Statistics categories
#categories_stats = ['games', 'minutes_90s', 'cards_red', 'cards_yellow']
#titles_stats = ['Number of games', 'Minutes Player / 90', 'Red Cards', 'Yellow Cards']

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

# Combine all categories and titles for complete visualization setup
categories = categories_passing + categories_set_piece + categories_gca + categories_shooting + categories_defense #+ categories_stats 
titles = titles_passing + titles_set_piece + titles_gca + titles_shooting + titles_defense # + titles_stats

# Standardize the data for each category for consistent visualization
for col in categories:
    df_standardised[col] = (sourceDF[col] - sourceDF[col].mean()) / sourceDF[col].std()

# Rename columns in the standardised DataFrame for better readability in visualization
df_standardised.rename(columns={categories[i]: titles[i] for i in range(len(categories))}, inplace=True)

# Adjust the values to start from the minimum value for each category
min_vals = df_standardised.min()
min_vals = df_standardised.min()
df_standardised[titles] = df_standardised[titles] - min_vals
# Add player names to the standardised DataFrame
df_standardised['player'] = sourceDF['player']


def getAppHeader():
    button = dcc.Link(children=[
        html.Span(className='icon', style={'background-image': 'url({})'.format(dash.get_asset_url('icons/check.png'))}),
        'Compare bookmarks'
    ], href='/bookmarks', id='compare_bookmarks')

    return html.Header([html.Img(id='header_logo', src=dash.get_asset_url('logo.png')),
        dcc.Link([fontIcon('chevron_left'), "Explore other candidates"], id='go_back', href='/')

    ])


def layout(player_id=None):
    # if not player_id:
    #     return "No player id has been passed. Please start by choosing a player from the start page."
    # player = sourceDF.iloc[[player_id]].to_dict(orient='records')[0]
    # chosen_player_position = player['position'] if 'position' in player else None
    # print(player)
    # print(player['position'])

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

            html.Div(id='columns', children=[
                addTabs(),
            ])
        ])
    ])



def addTabs():
    """
    Creates tabbed sections for the dashboard.
    Organizes different statistical categories into tabs for easier navigation.
    """
    return html.Div([
        dcc.Tabs(
            id="tabs-with-classes",
            value='tab-shooting',
            parent_className='custom-tabs',
            className='custom-tabs-container',
            children=[
                #dcc.Tab(
                #    label='Statistics',
                #    value='tab-stats',
                #    className='custom-tab',
                #    selected_className='custom-tab--selected'
                #),
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


def makeRadar(titles, bookmarkedPlayerIDS, chosen_player):
    """
    Generates a radar chart for the given player data.
    Visualizes various statistics of players in a radar chart format.
    """
    fig = go.Figure()

    # Chosen player
    fig.add_trace(go.Scatterpolar(
        theta=titles,
        r=[df_standardised[df_standardised['player'] == chosen_player['player']][var] for var in titles],
        fill='toself',
        name=chosen_player['player']
    ))

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
            )
        ),
        showlegend=True,
    )
    fig.update_layout(margin={'l': 400, 't': 40, 'b': 0, 'r': 0})

    return html.Div([
        dcc.Graph(figure=fig, config={'staticPlot': True})
    ])


# Callback functions for dynamic interactivity in the dashboard
@callback(Output('tabs-content-classes', 'children'),
    Input('tabs-with-classes', 'value'),
    Input('bookmarked_players', 'data'),
    Input('chosen_player', 'data'))
def render_content(tab, bookmarkedPlayerIDS, chosen_player):
    """
    Renders content based on the selected tab and bookmarked players.
    Updates the visualization based on user interactions with tabs and player data.
    """
    position = chosen_player['position']
    # Get list of bookmarked players
    bookmarkedPlayerIDS = list(set(bookmarkedPlayerIDS))
    bookmarkedPlayerIDS = [i for i in bookmarkedPlayerIDS if i != None]

    # Returns the appropriate radar chart
    #if tab == 'tab-stats':
    #    return makeRadar(titles_stats, bookmarkedPlayerIDS, chosen_player)
    if tab == 'tab-passing':
        return makeRadar(titles_passing, bookmarkedPlayerIDS, chosen_player)
    elif tab == 'tab-set-piece':
        return makeRadar(titles_set_piece, bookmarkedPlayerIDS, chosen_player)
    elif tab == 'tab-gca':
        return makeRadar(titles_gca, bookmarkedPlayerIDS, chosen_player)
    elif tab == 'tab-shooting':
        return makeRadar(titles_shooting, bookmarkedPlayerIDS, chosen_player)
    elif tab == 'tab-defense':
        return makeRadar(titles_defense, bookmarkedPlayerIDS, chosen_player)


def getPlayerImageElement(playerName):
    """
    Retrieves the HTML element for the player's image.

    :param playerName: The name of the player.
    :type playerName: str
    :return: HTML Div containing the player's image.
    """
    path = playerImageDirectory(playerName)
    if (path):
        image_path = get_first_vertical_image(path)
        return html.Div([html.Img(src=dash.get_asset_url(image_path)), ], className='player-image')
    else:
        return html.Div([html.Img(src=dash.get_asset_url('icons/player.png'))], className='invalid_image')


@callback(Output('chosen_player_box', 'children'), Input('chosen_player', 'data'))
def updateFirstPlaceHolder(chosenPlayer):
    """
    Updates the placeholder with chosen player details.
    Called when a new player is selected, updating the displayed information.
    """

    return [
        getPlayerImageElement(chosenPlayer['player']),
        html.Div(className='player-details', style={'borderLeft': '1px solid #ededed', 'paddingLeft': '12px'}, children=[
            html.H4(chosenPlayer['player'], className='chosen_player_name'),
            html.Div(className='separating-bar'),
            html.P('AGE: {}'.format(chosenPlayer['age']), className='chosen_player_age'),
            # html.P('HEIGHT: {}'.format(chosenPlayer['height_cm']), className='chosen_player_height'),
            html.P('FOULS: {}'.format(chosenPlayer['fouls']), className='chosen_player_fouls'),
            html.P('CARDS: yellow: {}, red: {}, yellow2: {}'.format(chosenPlayer['cards_yellow'], chosenPlayer['cards_red'], chosenPlayer['cards_yellow_red']), className='chosen_player_cards'),
        ])
    ]


@callback(
    Output('go_back', 'href'),
    Input('chosen_player_id', 'data')
)
def updateTargetOfGoBackLink(chosen_player_id):
    print(1)
    print('jddddddddddddddddddddddddddddddddd')
    return "replace/{}".format(chosen_player_id)


@callback(
    Output('tabs-with-classes', 'value'),
    Input('chosen_player', 'data'),
)
def set_default_tab(chosen_player):
    """
    Sets the default tab of the radar charts based on the chosen player's position.
    """
    if not chosen_player or 'position' not in chosen_player:
        return dash.no_update

    position = chosen_player['position']
    position_to_tab = {
        'MF': 'tab-passing',
        'DF': 'tab-defense',
        'FW': 'tab-gca',
        'GK': 'tab-defense'
    }
    default_tab = position_to_tab.get(position, 'tab-defense')

    return default_tab

