import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import os
import pandas as pd
from .components import specific_players
from .components import filters
import plotly.express as px


def getAgeYears(ageString):
    return int(ageString.split('-')[0])


files = ["player_shooting.csv", "player_defense.csv", "player_keepers.csv", "player_gca.csv", "player_possession.csv", "player_playingtime.csv", "player_passing.csv", "player_misc.csv"]
frames = []

counter = 0
for file in files:
    filePath = os.path.join(os.path.dirname(__file__), ('../data/' + file))

    frame = pd.read_csv(filePath)
    frames.append(frame)
    df = frames[0]
    for i in range(1, len(frames)):
        df = pd.merge(df, frames[i])

df['age'] = (df['age']).map(getAgeYears)  # This is the dataframe form which the plots are being applied. Applying filters will limit the rows in this object.
originalDf = df.copy()  # This is a global version of the original dataframe -> no filters will be applied on this

dash.register_page(__name__, path_template='/replace/<player_id>')

PLAYERID = None
PLAYER = None
POSITION = None


def layout(player_id=None):
    if not player_id:
        print('No `player_id` passed...')
        return ""  # TODO: handle this properly
    player = df.iloc[[player_id]].to_dict(orient='records')[0]
    global PLAYERID
    PLAYERID = player_id
    global PLAYER
    PLAYER = player
    global POSITION
    POSITION = player['position']
    return html.Div([html.Aside([filters.layout(originalDf), html.Div('hi', id='testing')], id='aside'), specific_players.specific_plots_component(player)], id='general_page')


# -------------------------------------------------------------
# Callbacks for when the age filter slide is changed: Dana
# -------------------------------------------------------------
@callback(Output('age_histogram', 'children'), Input('age_slider', 'value'))
def apply_age_filter(value):
    a = originalDf['age']
    mask = ((a >= value[0]) & (a <= value[1]))

    def map_in_bound(value):
        if (value):
            return "YES"
        return "NO"

    global df
    originalDf['in_bound'] = mask.map(map_in_bound)
    df = originalDf[originalDf['in_bound'] == "YES"]
    numberOfBins = len(a.unique())
    fig = px.histogram(originalDf, x="age", nbins=numberOfBins, color='in_bound', color_discrete_map={"YES": "#2196f3", "NO": "#E9E9E9"})
    fig.update_layout(yaxis_visible=False, xaxis_title=None, yaxis_showticklabels=False, xaxis_showticklabels=False, showlegend=False)
    fig.update_layout(margin={'l': 0, 't': 0, 'b': 0, 'r': 0}, plot_bgcolor='white')
    return dcc.Graph(figure=fig, config={'staticPlot': True}, style={'width': 'calc(100% - 20px)', 'height': '60px', 'margin': '5px auto'}),


# -------------------------------------------------------------
# Callbacks for general plots: Alexandru
# -------------------------------------------------------------
@callback([Output(component_id='graph1', component_property='figure'), Output(component_id='graph2', component_property='figure')], Input('age_slider', 'value'))  # Updates the position-specific plots based on the position
def update_output(ageRange):
    try:
        if POSITION == 'FW':
            fig1 = px.scatter(df, x='shots_on_target', y='goals', color=df['offsides'], title='Goal Scoring Efficiency', labels={'shots_on_target': 'Shots on target', 'goals': 'Goals', 'color': 'Number of Offsides'}, hover_data=['player'])
            fig1.update_layout(coloraxis_colorbar=dict(title='Number<br>of Offsides'  # Attempt to split the title into two lines
            ))
            fig2 = px.scatter(df, x='dribbles_completed', y='miscontrols', title='Ball Handling Skills', labels={'dribbles_completed': 'Dribbles Completed', 'miscontrols': 'Miscontrols'}, hover_data=['player'])

        elif POSITION == 'MF':
            fig1 = px.scatter(df, x='gca', y='passes_completed', title='Correlation Between Goal-Creating Actions and Passes Completed', labels={'x': 'Goal-Creating Actions', 'y': 'Passes completed'}, hover_data=['player'])
            fig2 = px.scatter(df, x='dribbles_completed', y='miscontrols', title='Ball Handling Skills', labels={'dribbles_completed': 'Dribbles Completed', 'miscontrols': 'Miscontrols'}, hover_data=['player'])

        elif POSITION == 'DF':
            fig1 = px.scatter(df, x='blocked_passes', y='clearances', title='Defensive Interventions', labels={'blocked_passes': 'Blocked passes', 'clearances': 'Clearances'}, hover_data=['player'])
            fig2 = px.scatter(df, x='tackles_won', y='interceptions', title="Analysing player's interception skills", labels={'tackles_won': 'Tackles won', 'interceptions': 'Interceptions'}, hover_data=['player'])

        else:  # POSITION==GK
            fig1 = px.scatter(df, x='gk_save_pct', y='gk_goals_against_per90', title='Goalkeeping Mastery: Balancing Saves and Goals Against')
            fig2 = px.scatter(df, x='gk_clean_sheets', y='age', title='Comparison of Age and Performance in Goalkeeping')

        return fig1, fig2

    except:
        return dash.no_update
