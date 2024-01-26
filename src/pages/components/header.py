import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash import callback
import os
import pandas as pd
from dataAdapters import getCountryFlagPath, playerImageDirectory, getPlayerTeam, get_first_vertical_image, getTeamGroup
from pages.helpers import fontIcon



filePath = os.path.join(os.path.dirname(__file__), ('../../data/' + 'merged_data.csv'))
sourceDF = pd.read_csv(filePath)





