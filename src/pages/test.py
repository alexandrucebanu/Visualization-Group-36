

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

cars_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/imports-85.csv')


# Build figure as FigureWidget
def get_parcat_fig(selected_index, cars_df):  # create function to update fig object
    # Build parcats dimensions
    categorical_dimensions = ['body-style', 'drive-wheels', 'fuel-type']
    dimensions = [dict(values=cars_df[label], label=label) for label in categorical_dimensions]

    color = np.zeros(len(cars_df), dtype='uint8')
    colorscale = [[0, 'gray'], [1, 'firebrick']]
    color[selected_index] = 1

    fig = go.FigureWidget(
        data=[go.Scatter(x=cars_df.horsepower, y=cars_df['highway-mpg'],
                         marker={'color': 'gray'}, mode='markers', selected={'marker': {'color': 'firebrick'}},
                         unselected={'marker': {'opacity': 0.3}}, selectedpoints=selected_index),
              go.Parcats(
                  domain={'y': [0, 0.4]}, dimensions=dimensions,
                  line={'colorscale': colorscale, 'cmin': 0,
                        'cmax': 1, 'color': color, 'shape': 'hspline'})
              ])

    fig.update_layout(
        height=800, xaxis={'title': 'Horsepower'},
        yaxis={'title': 'MPG', 'domain': [0.6, 1]},
        dragmode='lasso', hovermode='closest')
    return fig


app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Graph(
        id='parallel_category'
    )
])


@app.callback(
    Output("parallel_category", "figure"),
    Input("parallel_category", "selectedData"),
    Input("parallel_category", "clickData")
)
def get_fig_callback(selected_data, click_data):
    ctx = dash.callback_context
    if (ctx.triggered[0]['prop_id'] == "parallel_category.selectedData") \
            or (ctx.triggered[0]['prop_id'] == "parallel_category.clickData"):
        selected_data = [point['pointNumber'] for point in ctx.triggered[0]['value']['points']]
    else:
        selected_data = []
    return get_parcat_fig(selected_data, cars_df)


if __name__ == '__main__':
    app.run_server(debug=True)