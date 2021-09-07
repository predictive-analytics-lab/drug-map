import dash
from dash import dcc
from dash.dependencies import Input, Output, State
from dash import html
from flask import Flask
import os
import plotly
from flask_caching import Cache


from . import mapping

server = Flask('drug map')
server.secret_key = os.environ.get('secret_key', 'secret')

external_stylesheets = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/737dc4ab11f7a1a8d6b5645d26f69133d97062ae/dash-wind-streaming.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i",
                "https://codepen.io/chriddyp/pen/bWLwgP.css",
                ]

app = dash.Dash('Drug map', server=server, external_stylesheets=external_stylesheets)

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache'
})

# cache.clear() # remove when deploy

timeout = 60 * 60 * 24 * 7 # 7 days



def default_map() -> plotly.graph_objs.Figure:
    return mapping.args_to_map()
    

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

app.layout = html.Div([
    html.Div([
        html.H3("USA Drug Bias Map"),
    ], className='row', style={'text-align': "center"}),
    html.Div([
        html.Div([
            html.Div(html.Label(["Drug Type:",dcc.Dropdown(
                id='drugtype',
                options=[
                    {'label': 'Cannabis', 'value': 'cannabis'}],
                style={'width': '100%', 'display': 'block'},
                value='cannabis'
                )]),className="two columns"),
            html.Div(
                html.Label(["Map Type:",dcc.RadioItems(
            id='maptype',
            options=[
                {'label': 'Standard', 'value': 'standard'},
                {'label': '95% Confidence', 'value': 'confidence'},
            ],
            style={'width': '100%', 'display': 'block'},
            value='standard',
            )]),className="two columns")
        ],className='row', style={"padding":"2% 2%"}),
    
    html.Div(id='dd-output-container')
        ], className="row"
    ),
    dcc.Loading(id = "loading-icon", children=[html.Div([
            dcc.Graph(id="drug-map", figure=default_map(), style={"height":"70vh","width":"100%"}),
    ])], type="circle"),
    dcc.Slider(
        id='time-slider',
        min=2012,
        max=2019,
        step=1,
        value=2019,
        marks={year: str(year) for year in range(2012, 2020)}),
], style={'padding': '0px 10px 15px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "auto", "height": "90vh",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'})

@app.callback(Output('drug-map','figure'),[Input('drugtype','value'),Input('maptype','value'), Input('time-slider','value')])
@cache.memoize(timeout=timeout)
def update_graph(drugtype: str, maptype: str, time: int,) -> plotly.graph_objs.Figure:
    print(drugtype)
    print(maptype)
    print(time)

    fig = mapping.args_to_map(drug_type=drugtype, smoothed=False, map_type=maptype, year=time)
    # if relayout_data:
    #     if 'xaxis.range[0]' in relayout_data:
    #         fig['layout']['xaxis']['range'] = [
    #             relayout_data['xaxis.range[0]'],
    #             relayout_data['xaxis.range[1]']
    #         ]
    #     if 'yaxis.range[0]' in relayout_data:
    #         fig['layout']['yaxis']['range'] = [
    #             relayout_data['yaxis.range[0]'],
    #             relayout_data['yaxis.range[1]']
    #         ]
    return fig
    


# if __name__ == '__main__':
#     app.run_server(debug=False)