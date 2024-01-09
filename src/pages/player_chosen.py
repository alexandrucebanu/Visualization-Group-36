import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import os
import pandas as pd
from .components import specific_players
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
# print(frames)
for i in range(1, len(frames)):
    sourceDF = pd.merge(sourceDF, frames[i])

sourceDF['age'] = (sourceDF['age']).map(getAgeYears)  # This is the dataframe form which the plots are being applied. Applying filters will limit the rows in this object.


def getFilteredDF(filters):
    ## TODO: check if the filtering works as it should
    a = sourceDF['age']
    b = sourceDF['position']
    overallMask = ((a >= filters['age'][0]) & (a <= filters['age'][1]))
    positionMask = False
    chosenPositions = filters['chosen_positions']
    for chosenPosition in chosenPositions:
        positionMask = ((positionMask) | (b == chosenPosition))
    overallMask = (overallMask) & positionMask
    sourceDF['in_bound'] = overallMask.map(map_in_bound)
    return sourceDF[sourceDF['in_bound'] == "YES"]


dash.register_page(__name__, path_template='/replace/<player_id>')


def layout(player_id=None):
    if not player_id:
        print('No `player_id` passed...')
        return ""  # TODO: handle this properly
    player = sourceDF.iloc[[player_id]].to_dict(orient='records')[0]
    return html.Div([ dcc.Store('chosen_player', data=player, storage_type='local'), dcc.Store('filters', data={'position': player['position']}, storage_type='local'), html.Header([]),
        html.Section([html.Aside([html.Span('chevron_left', className='close-aside material-symbols-rounded'), filters.layout(sourceDF, player), html.Div('hi', id='testing')], id='aside'), specific_players.specific_plots_component(player)])], id='general_page')


def getPlayerById(playerId):
    return sourceDF.iloc[[playerId]].to_dict(orient='records')[0]


# -------------------------------------------------------------
# Callbacks for when the age filter slide is changed: Dana
# -------------------------------------------------------------
@callback(Output('age_histogram', 'children'), Output('filters', 'data'), Input('age_slider', 'value'), Input('chosen_positions', 'value'), Input('filters', 'data'))
def applyFilters(value, chosenPositions, filters):
    print(chosenPositions)
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
    return dcc.Graph(figure=fig, config={'staticPlot': True}, style={'width': 'calc(100% - 20px)', 'height': '60px', 'margin': '5px auto'}), newFilters


# -------------------------------------------------------------
# Callbacks for general plots: Alexandru
# -------------------------------------------------------------
@callback([Output(component_id='graph1', component_property='figure'), Output(component_id='graph2', component_property='figure')], Input('filters', 'data'), Input('chosen_player', 'data'))  # Updates the position-specific plots based on the position
def update_output(filters, chosenPlayer):
    filterDataFrame = getFilteredDF(filters)
    print('The positions available in the DF are: ', filterDataFrame['position'].unique())
    try:
        if chosenPlayer['position'] == 'FW':
            fig1 = px.scatter(filterDataFrame, x='shots_on_target', y='goals', color=filterDataFrame['offsides'], title='Goal Scoring Efficiency', labels={'shots_on_target': 'Shots on target', 'goals': 'Goals', 'color': 'Number of Offsides'}, hover_data=['player'])
            fig1.update_layout(coloraxis_colorbar=dict(title='Number of Offsides'))
            fig2 = px.scatter(filterDataFrame, x='dribbles_completed', y='miscontrols', title='Ball Handling Skills', labels={'dribbles_completed': 'Dribbles Completed', 'miscontrols': 'Miscontrols'}, hover_data=['player'])

        elif chosenPlayer['position'] == 'MF':
            fig1 = px.scatter(filterDataFrame, x='gca', y='passes_completed', title='Correlation Between Goal-Creating Actions and Passes Completed', labels={'x': 'Goal-Creating Actions', 'y': 'Passes completed'}, hover_data=['player'])
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
