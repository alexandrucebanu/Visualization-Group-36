import dash
from dash import html, dcc, callback, Output, Input
import os
import pandas as pd
from dataAdapters import getCountryFlagPath, playerImageDirectory, getPlayerTeam, get_first_vertical_image, getTeamGroup


dash.register_page(__name__, path_template='/replace/<player_id>')

filePath = os.path.join(os.path.dirname(__file__), '../data/player_gca.csv')
df_defense = pd.read_csv(filePath, encoding='utf-8')
playersList = [(index, player['player']) for index, player in df_defense.iterrows()]


def layout(player_id=None):
    if not player_id:
        return ""

    player = df_defense.iloc[[player_id]].to_dict(orient='records')[0]
    path = playerImageDirectory(player['player'])
    image_path = get_first_vertical_image(path)

    if image_path:
        return html.Div(
            id='player-image-container',
            className='player-chosen-container',
            children=[
                # Left half (player's image, name, and team flag)
                html.Div(
                    className='half',
                    children=[
                        # Player's image
                        html.Div([html.Img(src=dash.get_asset_url(image_path)), ], className='player-image'),
                        # Player's name
                        html.Div(f"Player: {player['player']}", className='player-name'),
                        # Team flag
                        html.Div([
                            html.Img(src=dash.get_asset_url(getCountryFlagPath(getPlayerTeam(player['player'])))),
                        ], className='team-flag'),
                    ]),

                # Separating bar
                html.Div(className='separating-bar'),

                # Right half (question mark and search bar)
                html.Div(
                    id='unknown-player-right',
                    className='half',
                    children=[
                        # Question mark image
                        html.Div([
                            html.Img(src=dash.get_asset_url('icons/unknown_user_right.svg'))], className='player-image'),

                        # Search bar
                        dcc.Dropdown(
                            id='select_player_name_chosen',
                            options=[{'label': playerItem[1], 'value': playerItem[0]} for playerItem in playersList],
                            placeholder="Search for a player...",
                        ),
                    ]
                ),

                # Selected player information outside of 'unknown-player-right'
                html.Div(
                    id='selected-player-info',
                    className='half',
                ),
            ]
        )
    else:
        # Handle the case when the image is not found
        return html.Div("Image not found")


# Callback to update content based on player ID
@callback(
    [Output('selected-player-info', 'children'),
     Output('unknown-player-right', 'style')],
    [Input('select_player_name_chosen', 'value')]
)
def update_selected_player_info(player_id):
    if player_id:
        player_id = int(player_id)
        player = df_defense.iloc[[player_id]].to_dict(orient='records')[0]
        path = playerImageDirectory(player['player'])
        image_path = get_first_vertical_image(path)

        if image_path:
            # Return the selected player information and hide the 'unknown-player-right'
            return [
                [
                    html.Div([html.Img(src=dash.get_asset_url(image_path)),], className='player-image'),
                    html.Div(f"Player: {player['player']}", className='player-name'),
                    html.Div([html.Img(src=dash.get_asset_url(getCountryFlagPath(getPlayerTeam(player['player'])))),], className='team-flag'),
                ],
                {'display': 'none'},  # Hide the 'unknown-player-right'
            ]

