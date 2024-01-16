import dash
from dash import html, dcc, callback, Output, Input
import os
import pandas as pd
from dataAdapters import getCountryFlagPath, playerImageDirectory, getPlayerTeam, get_first_vertical_image, getTeamGroup
from .components import specific_players
from .components import general_plots
from .components import filters
import plotly.express as px
from functools import reduce

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

def intervalMask(df, var, filters):
    a = df[var]
    mask = ((a >= filters[var][0]) & (a <= filters[var][1]))
    return mask

def getFilteredDF(filters):
    ## TODO: check if the filtering works as it should

    # position mask
    b = sourceDF['position']
    positionMask = False
    chosenPositions = filters['chosen_positions']
    for chosenPosition in chosenPositions:
        positionMask = ((positionMask) | (b == chosenPosition))

    # All interval masks
    variables = ['age', 'gca', 'passes_completed', 'tackles_won', 'interceptions']
    interval_masks = reduce(lambda x, y: x & y, [intervalMask(sourceDF, var, filters) for var in variables])
    
    # Return the filtered dataframe
    overallMask = (interval_masks) & positionMask
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
    newFilters = relayoutData_filtering(relayoutData_general1, newFilters, 'gca', 'passes_completed')
    newFilters = relayoutData_filtering(relayoutData_general2, newFilters, 'tackles_won', 'interceptions')

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
