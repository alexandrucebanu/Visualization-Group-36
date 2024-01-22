import dash
from dash import html, dcc, callback, Output, Input, State
import os
import pandas as pd
from dash.exceptions import PreventUpdate
from dataAdapters import getCountryFlagPath, playerImageDirectory, getPlayerTeam, get_first_vertical_image, getTeamGroup
from .components import specific_players
from .components import general_plots
from .components import filters
from .helper_functions import import_data
import plotly.express as px
from functools import reduce
from pages.components.header import getAppHeader
from pages.components import altered_general_page
from .helpers import fontIcon


sourceDF = import_data.importData()

possiblePositions = ['MF', 'DF', 'GK', 'FW']


def map_in_bound(value):
    if (value):
        return "YES"
    return "NO"


def intervalMask(df, var, filters):
    a = df[var]
    mask = ((a >= filters[var][0]) & (a <= filters[var][1]))
    return mask


def getFilteredDF(filters):
    ## TODO: check if the filtering works as it should

    # All interval masks
    variables = ['age', 'movement_sprint_speed', 'movement_reactions',

        # General plots
        'power_jumping', 'power_stamina',

        # Specific plots
        'shots_on_target', 'goals',
        'dribbles_completed', 'miscontrols',
        'gca', 'passes_completed',
        'dribbles_completed', 'miscontrols',
        'blocked_passes', 'clearances',
        'tackles_won', 'interceptions'
        # 'gk_save_pct', 'gk_goals_against_per90',
        # 'gk_clean_sheets', 'age'
    ]

    variables_relevant = [var for var in variables if var in filters.keys()]
    interval_masks = reduce(lambda x, y: x & y, [intervalMask(sourceDF, var, filters) for var in variables_relevant])

    # position mask
    a = sourceDF['position']
    positionMask = False
    chosenPositions = filters['chosen_positions']
    for chosenPosition in chosenPositions:
        positionMask = ((positionMask) | (a == chosenPosition))

    # foot preference mask
    b = sourceDF['preferred_foot']
    footMask = False
    preferredFoot = filters['preferred_foot']
    for preferredFoot in preferredFoot:
        footMask = ((footMask) | (b == preferredFoot))

    # Return the filtered dataframe
    overallMask = (interval_masks) & positionMask & footMask
    sourceDF['in_bound'] = overallMask.map(map_in_bound)
    sourceDF['id'] = sourceDF.index

    return sourceDF[sourceDF['in_bound'] == "YES"]


# Goal keeper data
filePath = os.path.join(os.path.dirname(__file__), '../data/player_gca.csv')
df_defense = pd.read_csv(filePath, encoding='utf-8')
playersList = [(index, player['player']) for index, player in df_defense.iterrows()]

dash.register_page(__name__, path_template='/replace/<player_id>')


def getPlayerImageElement(playerName):
    path = playerImageDirectory(playerName)
    if (path):
        image_path = get_first_vertical_image(path)
        return html.Div([html.Img(src=dash.get_asset_url(image_path)), ], className='player-image')
    else:
        return html.Div([html.Img(src=dash.get_asset_url('icons/player.png'))], className='invalid_image')


def playerInfoBox(player):
    return html.Div(id='player-image-container', className='player-chosen-container', children=
    [
        html.Div(className='half', children=[getPlayerImageElement(player['player']),
            html.Div(player['player'], className='player-name'),  # Team flag
            html.Div([html.Img(src=dash.get_asset_url(getCountryFlagPath(getPlayerTeam(player['player'])))), ], className='team-flag')
        ]
        ),  # Separating bar
        html.Div(className='separating-bar'),  # Right half (question mark and search bar)
        html.Div(id='clicked_player', className='half', children=[  # Question mark image
            html.Div([html.Img(id='unknown-player-icon', src=dash.get_asset_url('icons/magnifier.png'))], className='unknown-player-icon'),  # Search bar
            dcc.Dropdown(id='select_player_name_chosen', options=[{'label': playerItem[1], 'value': playerItem[0]} for playerItem in playersList], placeholder="Search for a player...", ), ]),

        # Selected player information outside 'clicked_player'
        html.Div(id='selected-player-info', children=[html.Button(id='bookmark_clicked', className='hidden')], className='half', ),
    ])
    # html.Div


def layout(player_id=None):
    if not player_id:
        return "No player id has been passed. Please start by choosing a player from the start page."
    player = sourceDF.iloc[[player_id]].to_dict(orient='records')[0]
    return html.Div(id='parent_player_chosen', children=[
        dcc.Store(id='clicked_player', storage_type='local'),
        dcc.Store(id='chosen_player', data=player, storage_type='local'),
        dcc.Store(id='chosen_player_id', data=int(player_id), storage_type='local'),
        dcc.Store(id='bookmarked_players', storage_type='local', data=[]),
        dcc.Store(id='filters', data={'position': player['position']}, storage_type='local'),
        getAppHeader(),
        html.Section([
            html.Aside(children=[
                html.Div(className='aside_content', children=[
                    playerInfoBox(player), filters.layout(sourceDF, player),
                ]), html.Span('chevron_left', id='close_aside', className='close-aside material-symbols-rounded')], id='aside'),
            html.Div(id='columns', children=[altered_general_page.main_page_changed(player)])
        ], id='general_page', className='player_chosen_show_aside')
    ])



# --------------------------------------------------------------------------------------------------------------------------
#####################################################      Callbacks      ##################################################
# --------------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------------
# Callback to toggle the left aside: Dana
# -------------------------------------------------------------
@callback(
    Output('general_page', 'className'),
    Input('close_aside', 'n_clicks'),
    State('general_page', 'className'),
    prevent_initial_call=True
)
def toggleAside(n_clicks, currentClass):
    if currentClass == "player_chosen_hide_aside":
        return "player_chosen_show_aside"
    return "player_chosen_hide_aside"



# -------------------------------------------------------------
# Callbacks to update player box based on chosen players: Akseniia
# -------------------------------------------------------------

@callback(
    Output('bookmarked_players', 'data', allow_duplicate=True),
    Input('clicked_player', 'n_clicks'), State('bookmarked_players', 'data'),
    State('clicked_player', 'data'),
    prevent_initial_call=True
)
def addBookmark(n_clicks, bookmarkedPlayerIDS, clickedPlayerID):
    if n_clicks == None:
        return dash.no_update
    return (bookmarkedPlayerIDS + [clickedPlayerID])
    return dash.no_update


@callback(
    Output('clicked_player', 'children'),
    Input('clicked_player', 'data'),
    prevent_initial_call=True
)
def updateClickedPlayer(clickedPlayerID):
    player = sourceDF.iloc[[clickedPlayerID]].to_dict(orient='records')[0]
    return [
        getPlayerImageElement(player['player']),
        html.Div(player['player'], className='player-name'),  # Team flag
        html.Div([html.Img(src=dash.get_asset_url(getCountryFlagPath(getPlayerTeam(player['player'])))), ], className='team-flag'),
        html.Button(id='bookmark_clicked_player', children=[fontIcon('star'), 'Bookmark'])
    ]


@callback(Output('clicked_player', 'data', allow_duplicate=True), Input('graph1', 'clickData'), prevent_initial_call=True)
def updateClickedPlayer(clickData):
    return int(sourceDF.index[sourceDF['player'] == clickData['points'][0]['customdata'][0]][0])



@callback(Output('clicked_player', 'data', allow_duplicate=True), Input('graph1_general', 'clickData'), prevent_initial_call=True)
def updateClickedPlayer(clickData):
    return int(sourceDF.index[sourceDF['player'] == clickData['points'][0]['customdata'][0]][0])


@callback(Output('clicked_player', 'data', allow_duplicate=True), Input('graph2_general', 'clickData'), prevent_initial_call=True)
def updateClickedPlayer(clickData):
    return int(sourceDF.index[sourceDF['player'] == clickData['points'][0]['customdata'][0]][0])




def getPlayerById(playerId):
    return sourceDF.iloc[[playerId]].to_dict(orient='records')[0]


def relayoutData_filtering(relayoutData, newFilters: dict, var1: str, var2: str):
    # General plots filtering, plot 1
    try:
        x_min = relayoutData['xaxis.range[0]']
        x_max = relayoutData['xaxis.range[1]']
        y_min = relayoutData['yaxis.range[0]']
        y_max = relayoutData['yaxis.range[1]']

        newFilters[var1] = [x_min, x_max]
        newFilters[var2] = [y_min, y_max]
    except:
        newFilters[var1] = [0, 10e4]
        newFilters[var2] = [0, 10e4]

    return newFilters


# -------------------------------------------------------------
# Callback for when the age filter slide is changed: Dana
# -------------------------------------------------------------
@callback(Output('age_histogram', 'children'), Output('filters', 'data'),
    Input('age_slider', 'value'),
    Input('chosen_positions', 'value'),
    Input('chosen_player', 'data'),
    Input('foot_preference', 'value'),
    Input('filters', 'data'),
    Input('graph1_general', 'relayoutData'),
    Input('graph2_general', 'relayoutData'),
)
def applyFilters(value, chosenPositions, chosenPlayer, footPreference, filters, relayoutData_general1, relayoutData_general2):
    a = sourceDF['age']
    mask = ((a >= value[0]) & (a <= value[1]))

    global df
    sourceDF['in_bound'] = mask.map(map_in_bound)

    # Age/wage histogram
    numberOfBins = len(a.unique())
    fig = px.histogram(sourceDF, x="age", nbins=numberOfBins, color='in_bound', color_discrete_map={"YES": "#2196f3", "NO": "#E9E9E9"})
    fig.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False, showlegend=False)
    fig.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')

    # Apply filters
    newFilters = filters
    newFilters['age'] = value
    newFilters['chosen_positions'] = chosenPositions
    newFilters['preferred_foot'] = footPreference

    parameter_list_general = [
        [relayoutData_general1, newFilters, 'movement_sprint_speed', 'power_stamina'],
        [relayoutData_general2, newFilters, 'power_jumping', 'movement_reactions']
    ]

    for params in parameter_list_general:
        newFilters = relayoutData_filtering(*params)

    return dcc.Graph(figure=fig, config={'staticPlot': True}, style={'width': 'calc(100% - 20px)', 'height': '60px', 'margin': '5px auto'}), newFilters


def getHumanReadableFeatureName(featureName):
    mapping = {
        'gca': 'goal creating actions'
    }
    if featureName in mapping.keys():
        featureName = mapping[featureName]
    return featureName.replace('_', ' ').title()





def getColorScale():
    colors = {
        "chosen": "rgb(95,175,1)",
        "bookmarked": "rgb(255,106,0)",
        "others": "rgb(14,69,96)"
    }
    # TODO: the following return is uglier than my high-school Arabic teacher. Fix it.
    return [(0.00, colors['others']), (0.4, colors['others']), (0.4, colors['bookmarked']), (0.6, colors['bookmarked']), (0.6, colors['chosen']), (1, colors['chosen'])]


# -------------------------------------------------------------
# Callbacks for position specific plot: Alexandru
# -------------------------------------------------------------
@callback(
    Output(component_id='graph1', component_property='figure'),
    Input('filters', 'data'),
    Input('chosen_player_id', 'data'),
    Input('attributes_dropdown', 'value'),
    Input('bookmarked_players', 'data'),
)
def updatePositionSpecificPlot(filters, chosen_player_id, chosenFeatures, bookmarkedPlayers):
    filteredDataFrame = getFilteredDF(filters)

    labels = {feature: getHumanReadableFeatureName(feature) for feature in chosenFeatures}

    filteredDataFrame['color'] = filteredDataFrame['id'].isin(list(bookmarkedPlayers)).map({True: 5, False: 1})
    filteredDataFrame.at[chosen_player_id, 'color'] = 10

    figure = px.parallel_coordinates(filteredDataFrame, height=700, color="color", range_color=[0, 10], dimensions=chosenFeatures, labels=labels, color_continuous_scale=getColorScale())
    figure.update_coloraxes(showscale=False)
    return figure





# -------------------------------------------------------------
# Callbacks to render general plots: Alicia
# -------------------------------------------------------------
@callback(
    Output(component_id='graph1_general', component_property='figure'),
    Output(component_id='graph2_general', component_property='figure'),
    Input('filters', 'data'),
    Input('bookmarked_players', 'data'),
    State('chosen_player_id', 'data'),
)  # Updates the general plots based on filter
def update_general_plots(filters, bookmarkedPlayers, chosen_player_id):
    filteredDataFrame = getFilteredDF(filters)

    # TODO: Change the parameters of the plots!
    filteredDataFrame['color'] = filteredDataFrame['id'].isin(list(bookmarkedPlayers)).map({True: 5, False: 1})
    filteredDataFrame.at[chosen_player_id, 'color'] = 10

    try:
        fig12 = px.scatter(filteredDataFrame, color="color", color_continuous_scale=getColorScale(), x="movement_sprint_speed", y='power_stamina', title='Sprint Speed and Stamina', labels={'movement_sprint_speed': 'Sprint Speed [FIFA scores]', 'power_stamina': 'Stamina [FIFA scores]'}, hover_data=['player'])
        fig22 = px.scatter(filteredDataFrame, color="color", color_continuous_scale=getColorScale(), x="power_jumping", y='movement_reactions', title='Power Jumping and Movement Reaction', labels={'power_jumping': 'Power Jumping [FIFA Scores]', 'movement_reactions': 'Movement Reactions [FIFA Scores]'}, hover_data=['player'])

        fig12.update_coloraxes(showscale=False)
        fig22.update_coloraxes(showscale=False)

        return fig12, fig22

    except:
        return dash.no_update



# -------------------------------------------------------------
# Callback to show the bookmarks' sidebar : Alicia
# -------------------------------------------------------------
@callback(
    Output('bookmarks_sidebar_back', 'style', allow_duplicate=True),
    Output('bookmarks_sidebar', 'style', allow_duplicate=True),
    Input('checkout', 'n_clicks'),
    State('bookmarks_sidebar_back', 'style'),
    prevent_initial_call=True
)
def update_output(n_clicks, style):
    if n_clicks >= 1:  # Show box on odd clicks
        style['right'] = '0';
        style['display'] = 'block'
    else:  # Hide box on even clicks
        style['right'] = '-500px';
        style['display'] = 'none'
    return style, style


# -------------------------------------------------------------
# Callback to hide bookmarks sidebar when clicked on the gray area : Dana
# -------------------------------------------------------------
@callback(
    Output('bookmarks_sidebar_back', 'style', allow_duplicate=True),
    Output('bookmarks_sidebar', 'style', allow_duplicate=True),
    Input('bookmarks_sidebar_back', 'n_clicks'),
    State('bookmarks_sidebar_back', 'style'),
    prevent_initial_call=True
)
def hideBookmarkedPlayersSidebar(n_clicks, style):
    style['display'] = 'none'
    return style, style



# -------------------------------------------------------------
# Callback to update the bookmarked players sidebar based on the latest bookmarks: Dana
# -------------------------------------------------------------
@callback(
    Output('bookmarks_sidebar_list', 'children'),
    Output('bookmarks_count', 'children'),
    Input('bookmarked_players', 'data')
)
def appendNewBookmarksToLists(bookmarkedPlayerIDS):
    bookmarkedPlayerIDS = list(set(bookmarkedPlayerIDS))
    bookmarkedPlayerIDS = [i for i in bookmarkedPlayerIDS if i != None]
    bookmarkedPlayers = sourceDF.iloc[bookmarkedPlayerIDS].to_dict(orient='records')
    if len(bookmarkedPlayers):
        return [
            html.Div(className='bookmarked_player', children=[player['player']])
            for player in bookmarkedPlayers
        ], len(bookmarkedPlayerIDS)
    return [html.Div(id='no_bookmarks_yet', children=[
        fontIcon('sentiment_neutral'),
        html.H4('No bookmarks yet!'),
    ])], 0



# -------------------------------------------------------------
# Callbacks for resetting the bookmarked players id list back to an empty list: Dana
# -------------------------------------------------------------
@callback(
    Output('bookmarked_players', 'data', allow_duplicate=True),
    Input('clear_bookmarks', 'n_clicks'),
    prevent_initial_call=True
)
def clearBookmarks(n_clicks):
    return []




# -------------------------------------------------------------
# Callbacks for adding the clicked player to bookmarks: Akseniia
# -------------------------------------------------------------
@callback(
    Output('bookmarked_players', 'data', allow_duplicate=True),
    Input('bookmark_clicked', 'n_clicks'),
    Input('clicked_player', 'data'),
    Input('bookmarked_players', 'data'),
    prevent_initial_call=True
)
def addPlayerToBookmarks(n_clicks, clickedPlayer, currentBookmarks):
    try:
        if n_clicks > 0:
            currentBookmarks += [clickedPlayer]
    except:
        return dash.no_update
    return list(set(currentBookmarks))
