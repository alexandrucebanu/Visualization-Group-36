import dash
from dash import html, dcc, callback, Output, Input
import os
import pandas as pd
from dataAdapters import getCountryFlagPath, playerImageDirectory, getPlayerTeam, get_first_vertical_image, getTeamGroup
from .components import specific_players
from .components import general_plots
from .components import filters
import plotly.express as px

possiblePositions = ['MF', 'DF', 'GK', 'FW'] 


def map_in_bound(value):
    if (value):
        return "YES"
    return "NO"


def getAgeYears(ageString):
    return int(ageString.split('-')[0])


files = ["player_shooting.csv", "player_defense.csv", "player_gca.csv", "player_possession.csv", "player_playingtime.csv", "player_passing.csv", "player_misc.csv"]
# TODO: bug: when including player_gca.csv the df will be sliced (as there are only 41 rows there) and we merge with it.
frames = []

counter = 0
for file in files:
    filePath = os.path.join(os.path.dirname(__file__), ('../data/' + file))
    frame = pd.read_csv(filePath)
    frames.append(frame)
sourceDF = frames[0]
for i in range(1, len(frames)):
    sourceDF = pd.merge(sourceDF, frames[i])

sourceDF['age'] = (sourceDF['age']).map(getAgeYears)  # This is the dataframe form which the plots are being applied. Applying filters will limit the rows in this object.


def getFilteredDF(filters):
    ## TODO: check if the filtering works as it should
    a = sourceDF['age']
    b = sourceDF['position']
    c = sourceDF['gca']
    d = sourceDF['passes_completed']
    e = sourceDF['tackles_won']
    f = sourceDF['interceptions']

    # Age mask
    overallMask = ((a >= filters['age'][0]) & (a <= filters['age'][1]))
    # position mask
    positionMask = False
    chosenPositions = filters['chosen_positions']
    for chosenPosition in chosenPositions:
        positionMask = ((positionMask) | (b == chosenPosition))

    # General plots filters, plot 1
    generalMask1 = ((c >= filters['gca'][0]) & (c <= filters['gca'][1]))
    generalMask2 = ((d >= filters['passes_completed'][0]) & (d <= filters['passes_completed'][1]))

    # General plots filters, plot 2
    generalMask3 = ((e >= filters['tackles_won'][0]) & (e <= filters['tackles_won'][1]))
    generalMask4 = ((f >= filters['interceptions'][0]) & (f <= filters['interceptions'][1]))
    
    # Overall mask
    overallMask = (overallMask) & positionMask & generalMask1 & generalMask2 & generalMask3 & generalMask4
    sourceDF['in_bound'] = overallMask.map(map_in_bound)
    return sourceDF[sourceDF['in_bound'] == "YES"]


filePath = os.path.join(os.path.dirname(__file__), '../data/player_gca.csv')
df_defense = pd.read_csv(filePath, encoding='utf-8')
playersList = [(index, player['player']) for index, player in df_defense.iterrows()]

dash.register_page(__name__, path_template='/replace/<player_id>')


def getPlayerImageElement(player):
    path = playerImageDirectory(player['player'])
    if (path):
        image_path = get_first_vertical_image(path)
        return html.Div([html.Img(src=dash.get_asset_url(image_path)), ], className='player-image')
    else:
        return html.Div([html.Img(src=dash.get_asset_url('icons/player.png'))], className='invalid_image')


def playerInfoBox(player):
    return html.Div(id='player-image-container', className='player-chosen-container', children=[html.Div(className='half', children=[getPlayerImageElement(player), html.Div(player['player'], className='player-name'),  # Team flag
        html.Div([html.Img(src=dash.get_asset_url(getCountryFlagPath(getPlayerTeam(player['player'])))), ], className='team-flag'), ]),  # Separating bar
        html.Div(className='separating-bar'),  # Right half (question mark and search bar)
        html.Div(id='unknown-player-right', className='half', children=[  # Question mark image
            html.Div([html.Img(src=dash.get_asset_url('icons/magnifier.png'))], className='unknown-player-icon'),  # Search bar
            dcc.Dropdown(id='select_player_name_chosen', options=[{'label': playerItem[1], 'value': playerItem[0]} for playerItem in playersList], placeholder="Search for a player...", ), ]),

        # Selected player information outside 'unknown-player-right'
        html.Div(id='selected-player-info', className='half', ), ])


def layout(player_id=None):
    if not player_id:
        return ""
    player = sourceDF.iloc[[player_id]].to_dict(orient='records')[0]
    return html.Div([dcc.Store('chosen_player', data=player, storage_type='local'), dcc.Store('filters', data={'position': player['position']}, storage_type='local'), html.Header([
        html.Img(id='header_logo',src=dash.get_asset_url('logo.png')),
    ]), html.Section(
        [html.Aside([playerInfoBox(player), html.Span('chevron_left', className='close-aside material-symbols-rounded'), filters.layout(sourceDF, player), html.Div('hi', id='testing')], id='aside'), html.Div(id='columns', children=[specific_players.specific_plots_component(player), general_plots.general_plots_component(), ])])],
        id='general_page')


# -------------------------------------------------------------
# Callbacks to update player box based on chosen players: Akseniia
# -------------------------------------------------------------
@callback([Output('selected-player-info', 'children'), Output('unknown-player-right', 'style')], [Input('select_player_name_chosen', 'value')])
def update_selected_player_info(player_id):
    if (player_id == None):
        return dash.no_update
    if player_id and player_id != None:
        player_id = int(player_id)
        player = df_defense.iloc[[player_id]].to_dict(orient='records')[0]
        path = playerImageDirectory(player['player'])
        image_path = get_first_vertical_image(path)

        if image_path:
            # Return the selected player information and hide the 'unknown-player-right'
            return [[html.Div([html.Img(src=dash.get_asset_url(image_path)), ], className='player-image'), html.Div(player['player'], className='player-name'), html.Div([html.Img(src=dash.get_asset_url(getCountryFlagPath(getPlayerTeam(player['player'])))), ], className='team-flag'), ], {'display': 'none'}, ]

        print('No `player_id` passed...')
        return dash.no_update  # TODO: handle this properly
    player = sourceDF.iloc[[player_id]].to_dict(orient='records')[0]
    return html.Div([dcc.Store('chosen_player', data=player, storage_type='local'), dcc.Store('filters', data={'position': player['position']}, storage_type='local'), html.Header([]),
        html.Section([html.Aside([html.Span('chevron_left', className='close-aside material-symbols-rounded'), filters.layout(sourceDF, player), html.Div('hi', id='testing')], id='aside'), specific_players.specific_plots_component(player)])], id='general_page')


def getPlayerById(playerId):
    return sourceDF.iloc[[playerId]].to_dict(orient='records')[0]


# -------------------------------------------------------------
# Callbacks for when the age filter slide is changed: Dana
# -------------------------------------------------------------
@callback(Output('age_histogram', 'children'), Output('filters', 'data'), 
            Input('age_slider', 'value'), Input('chosen_positions', 'value'), 
            Input('filters', 'data'), Input('graph1_general', 'relayoutData'),
            Input('graph2_general', 'relayoutData'))
def applyFilters(value, chosenPositions, filters, relayoutData_general1, relayoutData_general2):
    a = sourceDF['age']
    mask = ((a >= value[0]) & (a <= value[1]))

    global df
    sourceDF['in_bound'] = mask.map(map_in_bound)
    numberOfBins = len(a.unique())
    fig = px.histogram(sourceDF, x="age", nbins=numberOfBins, color='in_bound', color_discrete_map={"YES": "#2196f3", "NO": "#E9E9E9"})
    fig.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False, showlegend=False)
    fig.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')
    
    newFilters = filters
    newFilters['age'] = value
    newFilters['chosen_positions'] = chosenPositions

    # General plots filtering, plot 1
    try:
        x_min = relayoutData_general1['xaxis.range[0]']
        x_max = relayoutData_general1['xaxis.range[1]']
        y_min = relayoutData_general1['yaxis.range[0]']
        y_max = relayoutData_general1['yaxis.range[1]']

        newFilters['gca'] = [x_min, x_max]
        newFilters['passes_completed'] = [y_min, y_max]
    except:
        newFilters['gca'] = [0, 1000]
        newFilters['passes_completed'] = [0, 1000]

    # General plots filtering, plot 2
    try:
        x_min2 = relayoutData_general2['xaxis.range[0]']
        x_max2 = relayoutData_general2['xaxis.range[1]']
        y_min2 = relayoutData_general2['yaxis.range[0]']
        y_max2 = relayoutData_general2['yaxis.range[1]']

        newFilters['tackles_won'] = [x_min2, x_max2]
        newFilters['interceptions'] = [y_min2, y_max2]
    except:
        newFilters['tackles_won'] = [0, 1000]
        newFilters['interceptions'] = [0, 1000]

    return dcc.Graph(figure=fig, config={'staticPlot': True}, style={'width': 'calc(100% - 20px)', 'height': '60px', 'margin': '5px auto'}), newFilters


# -------------------------------------------------------------
# Callbacks for position specific plots: Alexandru
# -------------------------------------------------------------
@callback([Output(component_id='graph1', component_property='figure'), Output(component_id='graph2', component_property='figure')], Input('filters', 'data'), Input('chosen_player', 'data'))  # Updates the position-specific plots based on the position
def update_output(filters, chosenPlayer):
    filterDataFrame = getFilteredDF(filters)
    try:
        if chosenPlayer['position'] == 'FW':
            fig1 = px.scatter(filterDataFrame, x='shots_on_target', y='goals', color=filterDataFrame['offsides'], title='Goal Scoring Efficiency', labels={'shots_on_target': 'Shots on target', 'goals': 'Goals', 'color': 'Number of Offsides'}, hover_data=['player'])
            fig1.update_layout(coloraxis_colorbar=dict(title='Number of Offsides'))
            fig2 = px.scatter(filterDataFrame, x='dribbles_completed', y='miscontrols', title='Ball Handling Skills', labels={'dribbles_completed': 'Dribbles Completed', 'miscontrols': 'Miscontrols'}, hover_data=['player'])

        elif chosenPlayer['position'] == 'MF':
            fig1 = px.scatter(filterDataFrame, x='gca', y='passes_completed', title='Correlation Between Goal-Creating Actions and Passes Completed', labels={'gca': 'Goal-Creating Actions', 'passes_completed': 'Passes completed'}, hover_data=['player'])
            fig2 = px.scatter(filterDataFrame, x='dribbles_completed', y='miscontrols', title='Ball Handling Skills', labels={'dribbles_completed': 'Dribbles Completed', 'miscontrols': 'Miscontrols'}, hover_data=['player'])

        elif chosenPlayer['position'] == 'DF':
            fig1 = px.scatter(filterDataFrame, x='blocked_passes', y='clearances', title='Defensive Interventions', labels={'blocked_passes': 'Blocked passes', 'clearances': 'Clearances'}, hover_data=['player'])
            fig2 = px.scatter(filterDataFrame, x='tackles_won', y='interceptions', title="Analysing player's interception skills", labels={'tackles_won': 'Tackles won', 'interceptions': 'Interceptions'}, hover_data=['player'])

        else:  # POSITION==GK
            fig1 = px.scatter(filterDataFrame, x='gk_save_pct', y='gk_goals_against_per90', title='Goalkeeping Mastery: Balancing Saves and Goals Against')
            fig2 = px.scatter(filterDataFrame, x='gk_clean_sheets', y='age', title='Comparison of Age and Performance in Goalkeeping')

        return fig1, fig2

    except:
        return dash.no_update


# -------------------------------------------------------------
# Callbacks for general plots: Alicia
# -------------------------------------------------------------
@callback([Output(component_id='graph1_general', component_property='figure'), Output(component_id='graph2_general', component_property='figure')], 
            Input('filters', 'data'))  # Updates the general plots based on filter
def update_general_plots(filters):
    filterDataFrame = getFilteredDF(filters)

    # TODO: Change the parameters of the plots!
    try:
        fig12 = px.scatter(filterDataFrame, x="gca", y='passes_completed', title='Relation between agility and physical properties', labels={'x': 'Height x Weight [cm * kg]', 'y': 'Agility in Movement'}, hover_data=['player'])
        fig22 = px.scatter(filterDataFrame, x="tackles_won", y='interceptions', title='Relation between agility and physical properties', labels={'x': 'Height x Weight [cm * kg]', 'y': 'Agility in Movement'}, hover_data=['player'])

        return fig12, fig22

    except:
        return dash.no_update
