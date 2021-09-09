import dash
from dash import dcc
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import html
from flask import Flask
import os
import plotly
from flask_caching import Cache
import pandas as pd
import json

from . import mapping


server = Flask('drug map')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('Drug map', server=server)

cache = Cache()

cache_servers = os.environ.get('MEMCACHIER_SERVERS')
if cache_servers == None:
    cache.init_app(app.server, config={'CACHE_TYPE': 'simple'})
else:
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    cache.init_app(app.server,
        config={'CACHE_TYPE': 'saslmemcached',
                'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                'CACHE_MEMCACHED_USERNAME': cache_user,
                'CACHE_MEMCACHED_PASSWORD': cache_pass,
                'CACHE_OPTIONS': { 'behaviors': {
                    # Faster IO
                    'tcp_nodelay': True,
                    # Keep connection alive
                    'tcp_keepalive': True,
                    # Timeout for set/get requests
                    'connect_timeout': 2000, # ms
                    'send_timeout': 750 * 1000, # us
                    'receive_timeout': 750 * 1000, # us
                    '_poll_timeout': 2000, # ms
                    # Better failover
                    'ketama': True,
                    'remove_failed': 1,
                    'retry_timeout': 2,
                    'dead_timeout': 30}}})
# cache.clear() # remove when deploy

timeout = 60 * 60 * 24 * 7 # 7 days

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

app.layout = html.Div(
    children=[
        dcc.Store(id='clientside-data-store'),
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="three columns div-user-controls",
                    children=[
                        html.H2("USA DRUG BIAS MAP"),
                        html.P(
                            """Select different days using the date picker or by selecting
                            different time frames on the histogram."""
                        ),
                        html.Div(html.Label(["Drug Type:",dcc.Dropdown(
                        id='drugtype',
                        options=[
                            {'label': 'Cannabis', 'value': 'cannabis'}],
                        style={'width': '100%', 'display': 'block'},
                        value='cannabis'
                        )]),className="div-for-dropdown"),
                    html.Div(
                        html.Label(["Map Type:",dcc.RadioItems(
                    id='maptype',
                    options=[
                        {'label': 'Standard', 'value': 'standard'},
                        {'label': '95% Confidence', 'value': 'confidence'},
                    ],
                    style={'width': '100%', 'display': 'block'},
                    value='standard',
                    )]),className="div-for-dropdown"),
                    html.Div(
                        html.Label(["CI Type:",dcc.RadioItems(
                    id='citype',
                    options=[
                        {'label': 'Wilson Interval', 'value': 'wilson'},
                        # {'label': 'Bootstrap', 'value': 'bootstraps'},
                    ],
                    style={'width': '100%', 'display': 'block'},
                    value='wilson',
                    )]),className="div-for-dropdown"),
                    html.Div(
                        html.Label(["Usage Model:",dcc.RadioItems(
                    id='usagemodel',
                    options=[
                        {'label': 'Age, Race, Sex', 'value': 'normal'},
                        {'label': 'Age, Race, Sex, Poverty Status', 'value': 'poverty'},
                        {'label': 'Age, Race, Sex, Urban Area', 'value': 'urban'},
                    ],
                    style={'width': '100%', 'display': 'block'},
                    value='normal',
                    )]),className="div-for-dropdown"),
                    dcc.Markdown(
                        """
                        Source: NIBRS Drug Incidient Bias - Link to paper to be added.
                        
                        Links: [Source Code](https://github.com/predictive-analytics-lab/drug-map) | [Twitter] (https://twitter.com/WeArePal_ai)
                        """
                    ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="nine columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="drug-map", style={"height":"93vh"}),
                        dcc.Slider(
                            id='time-slider',
                            min=2012,
                            max=2019,
                            step=1,
                            value=2019,
                            marks={year: str(year) for year in range(2012, 2020)})
                    ],
                ),
            ],
        )
    ]
)


@app.callback(Output('clientside-data-store','data'),[Input('drugtype','value'),
                                           Input('usagemodel','value'),
                                           Input('citype','value'),
                                           Input('time-slider','value')])
@cache.memoize(timeout=timeout)
def update_store(drugtype: str, model: str, citype: str, time: int,) -> pd.DataFrame:
    df = mapping.args_to_df(drug_type=drugtype, smoothed=False, year=time, citype=citype, model=model)
    return df.reset_index().to_dict(orient='list')


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='get_map'
    ),
    Output('drug-map', 'figure'),
    Input('clientside-data-store', 'data'),
    Input('maptype', 'value')
)


# if __name__ == '__main__':
#     app.run_server(debug=False)