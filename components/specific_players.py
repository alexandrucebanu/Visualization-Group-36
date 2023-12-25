import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import os
import plotly.express as px

# Data
# --------------------------------------------------------------------------------------------------------------
# forward:
filePath_forward = os.path.join(os.path.dirname(__file__), '../notebooks/data/player_shooting.csv')
df_forward = pd.read_csv(filePath_forward)
filePath_misc = os.path.join(os.path.dirname(__file__), '../notebooks/data/player_misc.csv')
df_misc = pd.read_csv(filePath_misc)

# middle field:
filePath_midfield = os.path.join(os.path.dirname(__file__), '../notebooks/data/player_possession.csv')
df_midfield = pd.read_csv(filePath_midfield)
filePath_gca = os.path.join(os.path.dirname(__file__), '../notebooks/data/player_gca.csv')
df_gca = pd.read_csv(filePath_gca)
filePath_passes = os.path.join(os.path.dirname(__file__), '../notebooks/data/player_passing.csv')
df_passes = pd.read_csv(filePath_passes)

# defense:
filePath_defense = os.path.join(os.path.dirname(__file__), '../notebooks/data/player_defense.csv')
df_defense = pd.read_csv(filePath_defense)

# goal keeper:
filePath_gk = os.path.join(os.path.dirname(__file__), '../notebooks/data/player_keepers.csv')
df_goalkeeper = pd.read_csv(filePath_gk)

# App layout
# --------------------------------------------------------------------------------------------------------------

specific_plots_component = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id="page", style={'display': 'flex'},
             children=[
                 html.Div(id='selected_player_subpage', style={'display': 'flex'},
                          children=[
                              html.Br(),
                              html.Div(id='picture_of_soccer_player',
                                       children=[
                                           html.Div(id='the_actual_picture'),
                                           html.Div(id='pname', className='player-name', children=[])
                                       ]),
                              html.Br(),
                              html.Div(id='search_for_bookmarked_players',
                                       children=[
                                           html.Div(id='the_search_bar'),
                                           html.Div('Search', className='player-name-search')
                                       ])
                          ]),
                 html.Div(id='rectangle_specific_plots',
                          children=[
                              html.Div(id='position_container',
                                       style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
                                       children=[
                                           html.H3(id='position', children=[],
                                                   style={'color': '#243E4C', 'margin': '0', 'marginRight': '10px'}),
                                       ]),
                              html.Br(),
                              html.Div(id='graph_inside_rectangle',
                                       children=[
                                           dcc.Graph(id='graph1', figure={}, style={
                                               "box-shadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, "
                                                             "0, 0.19)",
                                               "borderRadius": "15px"})
                                       ]),
                              html.Br(),
                              html.Div(id='graph_inside_rectangle2',
                                       children=[
                                           dcc.Graph(id='graph2', figure={}, style={
                                               "box-shadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, "
                                                             "0, 0.19)",
                                               "borderRadius": "15px"})
                                       ])
                          ])
             ])
])


# ----------------------------------------------------------------------------------------------------------------------

# Callback
# --------------------------------------------------------------------------------------------------------------
@callback([Output(component_id='pname', component_property='children'),
           Output(component_id='position', component_property='children')],
          Input(component_id='url', component_property='pathname')
          )
def display_player_and_position(pathname):
    if pathname:
        # Extracting number from the URL path
        try:
            # Splitting the pathname by '/' and getting the last part
            number = int(pathname.strip("/").split("/")[-1])
            player_name = f"{df_defense.iloc[number]['player']}"
            player_position = df_defense.iloc[number]['position']
            if player_position == 'FW':
                player_position = 'Forward'
            elif player_position == 'MF':
                player_position = 'Middle Field'
            elif player_position == 'DF':
                player_position = 'Defender'
            else:
                player_position = 'Goalkeeper'
            return player_name, f"Position: {player_position}"
        except ValueError:
            # In case the URL does not contain a valid number
            return "No valid number in URL"
    else:
        return "URL not detected"


@callback(
    [Output(component_id='graph1', component_property='figure'),
     Output(component_id='graph2', component_property='figure')],
    [Input(component_id='url', component_property='pathname'),
     Input(component_id='position', component_property='children')]
)
def update_output(pathname, position):
    if pathname and position:
        try:
            player_id = int(pathname.strip("/").split("/")[-1])
            position_text = position.replace('Position: ', '')

            if position_text == 'Forward':
                df = df_forward
                fig1 = px.scatter(df, x='shots_on_target', y='goals', color=df_misc['offsides'],
                                  title='Goal Scoring Efficiency',
                                  labels={'shots_on_target': 'Shots on target', 'goals': 'Goals',
                                          'color': 'Number of Offsides'},
                                  hover_data=['player'])
                fig1.update_layout(coloraxis_colorbar=dict(
                    title='Number<br>of Offsides'  # Attempt to split the title into two lines
                ))
                fig2 = px.scatter(df_midfield, x='dribbles_completed', y='miscontrols',
                                  title='Ball Handling Skills',
                                  labels={'dribbles_completed': 'Dribbles Completed', 'miscontrols': 'Miscontrols'},
                                  hover_data=['player'])
                return fig1, fig2

            elif position_text == 'Middle Field':
                df = df_midfield
                fig1 = px.scatter(x=df_gca['gca'], y=df_passes['passes_completed'],
                                  title='Correlation Between Goal-Creating Actions and Passes Completed',
                                  labels={'x': 'Goal-Creating Actions', 'y': 'Passes completed'},
                                  hover_data=['player'])
                fig2 = px.scatter(df, x='dribbles_completed', y='miscontrols',
                                  title='Ball Handling Skills',
                                  labels={'dribbles_completed': 'Dribbles Completed', 'miscontrols': 'Miscontrols'},
                                  hover_data=['player'])
                return fig1, fig2

            elif position_text == 'Defender':
                df = df_defense
                fig1 = px.scatter(df, x='blocked_passes', y='clearances',
                                  title='Defensive Interventions',
                                  labels={'blocked_passes': 'Blocked passes', 'clearances': 'Clearances'},
                                  hover_data=['player'])
                fig2 = px.scatter(df, x='tackles_won', y='interceptions',
                                  title="Analysing player's interception skills",
                                  labels={'tackles_won': 'Tackles won', 'interceptions': 'Interceptions'},
                                  hover_data=['player'])
                return fig1, fig2

            elif position_text == 'Goalkeeper':
                df = df_goalkeeper
                fig1 = px.scatter(df, x='gk_save_pct', y='gk_goals_against_per90', title='Goalkeeping Mastery: Balancing Saves and Goals Against')
                fig2 = px.scatter(df, x='gk_clean_sheets', y='age', title='Comparison of Age and Performance in Goalkeeping')
                return fig1, fig2

            else:
                return {}, {}

        except (ValueError, IndexError):
            return dash.no_update
    else:
        return dash.no_update
# ----------------------------------------------------------------------------------------------------------------------
