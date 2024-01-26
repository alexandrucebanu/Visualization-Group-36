import dash
from dash import html, dcc, callback, Output, Input, State
import os
import pandas as pd
from dash.exceptions import PreventUpdate
from dataAdapters import getCountryFlagPath, playerImageDirectory, getPlayerTeam, get_first_vertical_image, getTeamGroup
from .components import specific_players
from .components import general_plots
from .components import filters
import plotly.express as px
from functools import reduce
from pages.components import altered_general_page
from .helpers import fontIcon

# Setting up the file path for the merged data CSV file
filePath = os.path.join(os.path.dirname(__file__), ('../data/' + 'merged_data.csv'))
sourceDF = pd.read_csv(filePath)

# Defining possible positions in the dataset
possiblePositions = ['MF', 'DF', 'GK', 'FW']


def map_in_bound(value):
    """
    Maps a boolean value to a string representation.

    :param value: The boolean value to map.
    :type value: bool
    :return: "YES" if value is True, otherwise "NO".
    :rtype: str
    """
    if (value):
        return "YES"
    return "NO"


def intervalMask(df, var, filters):
    """
    Creates a mask for filtering DataFrame based on a variable's interval.

    :param df: The DataFrame to apply the mask.
    :param var: The variable to filter on.
    :param filters: The filters specifying the interval.
    :return: The mask for the specified interval.
    """
    a = df[var]
    mask = ((a >= filters[var][0]) & (a <= filters[var][1]))
    return mask


def getFilteredDF(filters):
    """
    Applies filters to the DataFrame and returns the filtered DataFrame.

    :param filters: Dictionary containing filter settings.
    :return: Filtered DataFrame.
    """
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
    preferredFoot_filter = filters['preferred_foot']
    for preferredFoot in preferredFoot_filter:
        footMask = ((footMask) | (b == preferredFoot))

    # Return the filtered dataframe
    overallMask = (interval_masks) & positionMask & footMask
    sourceDF['in_bound'] = overallMask.map(map_in_bound)
    sourceDF['id'] = sourceDF.index

    return sourceDF[sourceDF['in_bound'] == "YES"]


# GCA data
filePath = os.path.join(os.path.dirname(__file__), '../data/player_gca.csv')
df_defense = pd.read_csv(filePath, encoding='utf-8')
playersList = [(index, player['player']) for index, player in df_defense.iterrows()]

dash.register_page(__name__, path_template='/replace/<player_id>')


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


def playerInfoBox(player):
    """
    Creates an information box for a given player.

    :param player: The player data dictionary.
    :type player: dict
    :return: HTML Div containing the player information box.
    """
    return html.Div(id='player-image-container', className='player-chosen-container', children=
    [
        html.Div(className='half', children=[getPlayerImageElement(player['player']),
            html.Div(player['player'], className='player-name'),  # Team flag
            html.Div([html.Img(src=dash.get_asset_url(
                getCountryFlagPath(getPlayerTeam(player['player'])))), ],
                className='team-flag')
        ]
        ),  # Separating bar
        html.Div(className='separating-bar'),  # Right half (question mark and search bar)
        html.Div(id='clicked_player', className='half', children=[  # Question mark image
            html.Div([html.Img(id='unknown-player-icon', src=dash.get_asset_url('icons/magnifier.png'))],
                className='unknown-player-icon'),  # Search bar
            dcc.Dropdown(id='select_player_name_chosen',
                options=[{'label': playerItem[1], 'value': playerItem[0]} for playerItem in playersList],
                placeholder="Search for a player...", ),
            html.Button(id='bookmark_clicked_player', className='hidden')
        ]),

        # Selected player information outside 'clicked_player'
        html.Div(id='selected-player-info', children=[html.Button(id='bookmark_clicked', className='hidden')],
            className='half', ),
    ])
    # html.Div


def getAppHeader():
    button = dcc.Link(children=[
        html.Span(className='icon', style={'background-image': 'url({})'.format(dash.get_asset_url('icons/check.png'))}),
        'Compare bookmarks'
    ], href='/bookmarks', id='compare_bookmarks')
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
                button
            ]),

    ])


def layout(player_id=None):
    """
    Defines the layout of the 'player chosen' page.

    :param player_id: The ID of the player to display.
    :type player_id: int
    :return: The HTML layout for the page.
    """
    if not player_id:
        return "No player id has been passed. Please start by choosing a player from the start page."
    player = sourceDF.iloc[[player_id]].to_dict(orient='records')[0]
    return html.Div(id='parent_player_chosen', children=[
        dcc.Store(id='clicked_player_id', storage_type='local'),
        dcc.Store(id='chosen_player', data=player, storage_type='local'),
        dcc.Store(id='chosen_player_id', data=int(player_id), storage_type='local'),
        dcc.Store(id='bookmarked_players', storage_type='local', data=[]),
        dcc.Store(id='filters', data={'position': player['position']}, storage_type='local'),
        getAppHeader(),
        html.Section([
            html.Aside(children=[
                html.Div(className='aside_content', children=[
                    playerInfoBox(player), filters.layout(sourceDF, player),
                ]), html.Span('chevron_left', id='close_aside', className='close-aside material-symbols-rounded')],
                id='aside'),
            html.Div(id='columns', children=[altered_general_page.main_page_changed(player, getColorMap())]),

        ], id='general_page', className='player_chosen_show_aside')
    ])


# --------------------------------------------------------------------------------------------------------------------------
#####################################################      Callbacks      ##################################################
# --------------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------------
# Callback to toggle the left aside: Dana
# -------------------------------------------------------------

# Callback to toggle the left aside
@callback(
    Output('general_page', 'className'),
    Input('close_aside', 'n_clicks'),
    State('general_page', 'className'),
    prevent_initial_call=True
)
def toggleAside(n_clicks, currentClass):
    """
    Toggles the visibility of the left aside (sidebar) on the page.

    :param n_clicks: Number of clicks on the toggle button.
    :param currentClass: Current CSS class of the general page.
    :return: The updated CSS class for the general page.
    """
    if currentClass == "player_chosen_hide_aside":
        return "player_chosen_show_aside"
    return "player_chosen_hide_aside"


# -------------------------------------------------------------
# Callbacks to update player box based on chosen players: Akseniia
# -------------------------------------------------------------

# Callbacks to update player box based on chosen players
@callback(
    Output('bookmarked_players', 'data', allow_duplicate=True),
    Input('bookmark_clicked_player', 'n_clicks'), State('bookmarked_players', 'data'),
    State('clicked_player_id', 'data'),
    prevent_initial_call=True
)
def addBookmark(n_clicks, bookmarkedPlayerIDS, clickedPlayerID):
    """
    Adds a player to the list of bookmarked players.

    :param n_clicks: Number of clicks on the bookmark button.
    :param bookmarkedPlayerIDS: Current list of bookmarked player IDs.
    :param clickedPlayerID: ID of the player to bookmark.
    :return: Updated list of bookmarked player IDs.
    """
    if n_clicks == None:
        return dash.no_update
    return (bookmarkedPlayerIDS + [clickedPlayerID])
    return dash.no_update


def renderClickPlayerBox(clickedPlayerId, bookmarks=[]):
    buttonElement = html.Button(id='bookmark_clicked_player', children=[fontIcon('star'), 'Bookmark'])

    if clickedPlayerId in bookmarks:
        buttonElement = html.Button(id='bookmark_clicked_player', className='bookmarked', children=[fontIcon('star'), 'Bookmarked'])
    player = sourceDF.iloc[clickedPlayerId]
    return [
        getPlayerImageElement(player['player']),
        html.Div(player['player'], className='player-name'),  # Team flag
        html.Div([html.Img(src=dash.get_asset_url(getCountryFlagPath(getPlayerTeam(player['player'])))), ],
            className='team-flag'),
        buttonElement
    ]


# Callback for updating the clicked player's information
@callback(
    Output('clicked_player', 'children'),
    Input('clicked_player_id', 'data'),
    State('bookmarked_players', 'data'),
    prevent_initial_call=True)
def updateClickedPlayer(clickedPlayerID, bookmarks):
    """
    Updates the clicked player's information based on their ID.

    :param clickedPlayerID: The ID of the clicked player.
    :type clickedPlayerID: int
    :return: HTML content for the clicked player.
    """
    return renderClickPlayerBox(clickedPlayerID, bookmarks)


# Callbacks for updating the clicked player based on graph interactions
@callback(Output('clicked_player_id', 'data', allow_duplicate=True), Input('graph1', 'clickData'),
    prevent_initial_call=True)
def updateClickedPlayer(clickData):
    """
    Updates the clicked player's ID based on the click event on the first graph.

    :param clickData: Data from the click event on the graph.
    :type clickData: dict
    :return: The ID of the clicked player.
    """
    return int(sourceDF.index[sourceDF['player'] == clickData['points'][0]['customdata'][0]][0])


@callback(Output('clicked_player_id', 'data', allow_duplicate=True), Input('graph1_general', 'clickData'),
    prevent_initial_call=True)
def updateClickedPlayer(clickData):
    """
    Updates the clicked player's ID based on the click event on the first general graph.

    :param clickData: Data from the click event on the general graph.
    :type clickData: dict
    :return: The ID of the clicked player.
    """
    return int(sourceDF.index[sourceDF['player'] == clickData['points'][0]['customdata'][0]][0])


@callback(Output('clicked_player_id', 'data', allow_duplicate=True), Input('graph2_general', 'clickData'),
    prevent_initial_call=True)
def updateClickedPlayer(clickData):
    """
    Updates the clicked player's ID based on the click event on the second general graph.

    :param clickData: Data from the click event on the general graph.
    :type clickData: dict
    :return: The ID of the clicked player.
    """
    return int(sourceDF.index[sourceDF['player'] == clickData['points'][0]['customdata'][0]][0])


@callback(
    Output('clicked_player_id', 'data', allow_duplicate=True),
    Input('select_player_name_chosen', 'value'),
    prevent_initial_call=True
)
def updateClickedPlayer(player_id):
    """
    Updates the clicked player's ID based on the player selected from the dropdown.

    :param player_id: The ID of the player selected from the dropdown.
    :type player_id: int
    :return: The ID of the selected player.
    """
    return int(player_id)


# Utility function to get player data by ID
def getPlayerById(playerId):
    """
    Retrieves player data by player ID.

    :param playerId: The ID of the player.
    :type playerId: int
    :return: Dictionary of player data.
    """
    return sourceDF.iloc[[playerId]].to_dict(orient='records')[0]


# Function to filter data based on plot interactions
def relayoutData_filtering(relayoutData, newFilters: dict, var1: str, var2: str):
    """
    Filters data based on user interaction with plot layouts.

    :param relayoutData: Data from plot interaction.
    :param newFilters: Existing filters to update.
    :param var1: The first variable to filter on.
    :param var2: The second variable to filter on.
    :return: Updated filters.
    """
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
# Callback for applying filters based on user input: Dana
# -------------------------------------------------------------
@callback(
    Output('age_histogram', 'children'),
    Output('wage_histogram', 'children'),
    Output('filters', 'data'),
    Input('age_slider', 'value'),
    Input('wage_slider', 'value'),
    Input('chosen_positions', 'value'),
    Input('chosen_player', 'data'),
    Input('foot_preference', 'value'),
    Input('filters', 'data'),
    Input('graph1_general', 'relayoutData'),
    Input('graph2_general', 'relayoutData'),
)
def applyFilters(value, wageRange, chosenPositions, chosenPlayer, footPreference, filters, relayoutData_general1,
        relayoutData_general2):
    """
    Applies filters to the data based on user input from various UI components.

    :param value: Age range from the slider.
    :param wageRange: Wage range from the slider.
    :param chosenPositions: Selected player positions.
    :param chosenPlayer: Data of the chosen player.
    :param footPreference: Preferred foot filter.
    :param filters: Existing filters.
    :param relayoutData_general1: Interaction data from the first general plot.
    :param relayoutData_general2: Interaction data from the second general plot.
    :return: Updated age and wage histograms, and filters.
    """
    a = sourceDF['age']
    mask = ((a >= value[0]) & (a <= value[1]))

    wageSeries = sourceDF['wage_eur'].dropna()
    maskWage = ((wageSeries >= wageRange[0]) & (wageSeries <= wageRange[1]))

    global df
    sourceDF['in_bound'] = mask.map(map_in_bound)
    sourceDF['in_bound_wage'] = maskWage.map(map_in_bound)

    # Age/wage histogram
    numberOfBins = len(a.unique())
    figAge = px.histogram(sourceDF, x="age", nbins=numberOfBins, color='in_bound',
        color_discrete_map={"YES": "#2196f3", "NO": "#E9E9E9"})
    figAge.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False,
        showlegend=False)
    figAge.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')

    figWage = px.histogram(sourceDF, x="wage_eur", nbins=10, color='in_bound_wage',
        color_discrete_map={"YES": "#2196f3", "NO": "#E9E9E9"})
    figWage.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False,
        showlegend=False)
    figWage.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')

    # Apply filters
    newFilters = filters
    newFilters['age'] = value
    newFilters['chosen_positions'] = chosenPositions
    newFilters['preferred_foot'] = footPreference
    newFilters['wage'] = wageRange

    parameter_list_general = [
        [relayoutData_general1, newFilters, 'movement_sprint_speed', 'power_stamina'],
        [relayoutData_general2, newFilters, 'power_jumping', 'movement_reactions']
    ]

    for params in parameter_list_general:
        newFilters = relayoutData_filtering(*params)

    ageGraph = dcc.Graph(figure=figAge, config={'staticPlot': True},
        style={'width': 'calc(100% - 20px)', 'height': '60px', 'margin': '5px auto'})
    wageGraph = dcc.Graph(figure=figWage, config={'staticPlot': True},
        style={'width': 'calc(100% - 20px)', 'height': '60px', 'margin': '5px auto'})
    return ageGraph, wageGraph, newFilters


def getHumanReadableFeatureName(featureName):
    """
    Converts a feature name to a human-readable format.

    :param featureName: The original feature name.
    :type featureName: str
    :return: The human-readable feature name.
    """
    mapping = {
        'gca': 'goal creating actions'
    }
    if featureName in mapping.keys():
        featureName = mapping[featureName]
    return featureName.replace('_', ' ').title()


def getColorMap():
    return {
        "chosen": "rgb(95,175,1)",
        "bookmarked": "rgb(255,106,0)",
        "candidate": "rgb(255,193,7)",
        "others": "rgb(14,69,96)"
    }


def getColorScale():
    """
    Generates a color scale for data visualization.

    :return: A color scale for Plotly graphs.
    """
    colors = getColorMap()
    # TODO: the following return is uglier than my high-school Arabic teacher. Fix it.
    return [(0.00, colors['others']), (0.4, colors['others']), (0.4, colors['candidate']), (0.5, colors['candidate']), (0.5, colors['bookmarked']), (0.6, colors['bookmarked']),
        (0.6, colors['chosen']), (1, colors['chosen'])]


# -------------------------------------------------------------
# Callbacks for position specific plot: Alexandru
# -------------------------------------------------------------
@callback(
    Output(component_id='graph1', component_property='figure'),
    Input('filters', 'data'),
    Input('chosen_player_id', 'data'),
    Input('attributes_dropdown', 'value'),
    Input('bookmarked_players', 'data'),
    Input('clicked_player_id', 'data'),
)
def updatePositionSpecificPlot(filters, chosen_player_id, chosenFeatures, bookmarkedPlayers,clickedPlayerId):
    """
    Updates the position-specific plot based on selected filters and bookmarked players.

    :param filters: Applied filters.
    :param chosen_player_id: ID of the chosen player.
    :param chosenFeatures: Selected features for the plot.
    :param bookmarkedPlayers: List of bookmarked player IDs.
    :return: Updated position-specific plot.
    """
    filteredDataFrame = getFilteredDF(filters)

    labels = {feature: getHumanReadableFeatureName(feature) for feature in chosenFeatures}

    filteredDataFrame['color'] = 0
    filteredDataFrame['color'][filteredDataFrame['id'] == int(clickedPlayerId)] = 4.5
    maskForBookmarks = filteredDataFrame['id'].isin(list(bookmarkedPlayers))
    filteredDataFrame['color'][maskForBookmarks] = 5.5
    filteredDataFrame['color'][filteredDataFrame['id']==chosen_player_id] = 10


    # fig = px.parallel_categories(filteredDataFrame,dimensions=chosenFeatures)
    # return fig
    # return px.parallel_categories(filteredDataFrame)

    figure = px.parallel_coordinates(filteredDataFrame, height=600, color="color", range_color=[0, 10],
        dimensions=chosenFeatures, labels=labels, color_continuous_scale=getColorScale())
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
    Input('clicked_player_id', 'data'),
    State('chosen_player_id', 'data'),
)  # Updates the general plots based on filter
def update_general_plots(filters, bookmarkedPlayers, clickedPlayerId, chosen_player_id):
    """
    Updates the general plots based on the current filters, bookmarked players, and the chosen player.

    :param filters: Dictionary of filters applied to the data.
    :param bookmarkedPlayers: List of IDs of bookmarked players.
    :param chosen_player_id: ID of the currently chosen player.
    :return: Two Plotly figure objects for the updated plots.
    """
    filteredDataFrame = getFilteredDF(filters)

    # TODO: Change the parameters of the plots!
    filteredDataFrame['color'] = 0

    filteredDataFrame['color'][filteredDataFrame['id'] == int(clickedPlayerId)] = 4.5
    maskForBookmarks = filteredDataFrame['id'].isin(list(bookmarkedPlayers))
    filteredDataFrame['color'][maskForBookmarks] = 5.5
    filteredDataFrame['color'][filteredDataFrame['id']==chosen_player_id] = 10



    try:
        fig12 = px.scatter(filteredDataFrame, color="color", color_continuous_scale=getColorScale(),
            x="movement_sprint_speed", y='power_stamina', title='Sprint Speed and Stamina',
            labels={'movement_sprint_speed': 'Sprint Speed [FIFA scores]',
                'power_stamina': 'Stamina [FIFA scores]'}, hover_data=['player'])
        fig22 = px.scatter(filteredDataFrame, color="color", color_continuous_scale=getColorScale(), x="power_jumping",
            y='movement_reactions', title='Power Jumping and Movement Reaction',
            labels={'power_jumping': 'Power Jumping [FIFA Scores]',
                'movement_reactions': 'Movement Reactions [FIFA Scores]'}, hover_data=['player'])

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
    """
    Toggles the display of the bookmarks sidebar based on user interaction.

    :param n_clicks: The number of clicks on the checkout button.
    :param style: The current CSS style of the bookmarks' sidebar.
    :return: Updated CSS style for the sidebar and its background layer.
    """
    if n_clicks >= 1:  # Show box on odd clicks
        style['right'] = '0'
        style['display'] = 'block'
    else:  # Hide box on even clicks
        style['right'] = '-500px'
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
    """
    Hides the bookmarks sidebar when the gray area (background) is clicked.

    :param n_clicks: Number of clicks on the gray background area.
    :param style: Current CSS style of the bookmarks sidebar.
    :return: Updated CSS style to hide the sidebar and its background layer.
    """
    style['display'] = 'none'
    return style, style



# -------------------------------------------------------------
# Callbacks for resetting the bookmarked players id list back to an empty list: Dana
# -------------------------------------------------------------
@callback(
    Output('bookmarked_players', 'data', allow_duplicate=True),
    Input('clear_bookmarks', 'n_clicks'),
    prevent_initial_call=True
)
def clearBookmarks(n_clicks):
    """
    Clears all bookmarked players.

    :param n_clicks: Number of clicks on the clear bookmarks button.
    :return: An empty list (resetting bookmarks).
    """
    return []




# -------------------------------------------------------------
# Update the clicked player box accordingly after adding a bookmark: Dana
# -------------------------------------------------------------
@callback(Output('clicked_player', 'children', allow_duplicate=True), Input('bookmarked_players', 'data'), State('clicked_player_id', 'data'), prevent_initial_call=True)
def updateClickedPlayerBox(bookmarks, clicked_player_id):
    return renderClickPlayerBox(clicked_player_id, bookmarks)


# -------------------------------------------------------------
# Callbacks for adding the clicked player to bookmarks: Akseniia
# -------------------------------------------------------------
@callback(
    Output('bookmarked_players', 'data', allow_duplicate=True),
    Input('bookmark_clicked', 'n_clicks'),
    Input('clicked_player_id', 'data'),
    State('bookmarked_players', 'data'),
    prevent_initial_call=True
)
def addPlayerToBookmarks(n_clicks, clickedPlayer, currentBookmarks):
    """
    Adds the clicked player to the list of bookmarked players.

    :param n_clicks: Number of clicks on the bookmark button.
    :param clickedPlayer: Data of the player that was clicked.
    :param currentBookmarks: Current list of bookmarked players' IDs.
    :return: Updated list of bookmarked players' IDs.
    """
    try:
        if n_clicks > 0:
            currentBookmarks += [clickedPlayer]
    except:
        return dash.no_update
    return list(set(currentBookmarks))


# -------------------------------------------------------------
# Callback to update the bookmarked players sidebar and the navigator link (to bookmarks page) based on the latest bookmarks: Dana
# -------------------------------------------------------------
@callback(
    Output('bookmarks_sidebar_list', 'children'),
    Output('bookmarks_count', 'children'),
    Output('compare_bookmarks', 'className'),
    Input('bookmarked_players', 'data')
)
def appendNewBookmarksToLists(bookmarkedPlayerIDS):
    """
    Updates the sidebar with the list of bookmarked players and the bookmark count.

    :param bookmarkedPlayerIDS: List of IDs of bookmarked players.
    :return: Updated list of bookmarked players, count of bookmarked players, and class name for comparison button.
    """
    bookmarkedPlayerIDS = list(set(bookmarkedPlayerIDS))
    bookmarkedPlayerIDS = [i for i in bookmarkedPlayerIDS if i != None]
    bookmarkedPlayers = sourceDF.iloc[bookmarkedPlayerIDS].to_dict(orient='records')
    if len(bookmarkedPlayers):
        return (
            [
                html.Div(className='bookmarked_player', children=[
                    player['player'],
                    html.Img(src=dash.get_asset_url(getCountryFlagPath(getPlayerTeam(player['player']))))
                    , html.Span("{} y.o".format(player['age']), className='playerAge')
                ])
                for player in bookmarkedPlayers
            ],
            len(bookmarkedPlayerIDS),
            'visible')
    return [html.Div(id='no_bookmarks_yet', children=[
        fontIcon('sentiment_neutral'),
        html.H4('No bookmarks yet!'),
    ])], 0, 'hidden'
