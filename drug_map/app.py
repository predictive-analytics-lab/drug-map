from typing import List
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

mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
app.scripts.append_script({ 'external_url' : mathjax })

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
cache.clear() # remove when deploy

timeout = 60 * 60 * 24 * 7 # 7 days

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })
            # html.Div(html.Label(["Geospatial Smoothing:", 
            #             dcc.RadioItems(
            #                 id='smoothing',
            #                 options=[
            #                 {'label': 'On', 'value': 'on'},
            #                 {'label': 'Off', 'value': 'off'},
            #                 ],
            #             style={'width': '100%', 'display': 'block'},
            #             value='off'
            #             )]),className="div-for-dropdown"),    

base_ui = html.Div(className="",
    children=[
        dcc.RadioItems(id='urbanfilter', value="2", style = dict(display='none')),
        dcc.RadioItems(id='smoothingparameter', value="1.0", style = dict(display='none')),
        html.H2("USA DRUG BIAS MAP"),
        html.P(
            """Select different drugs, as well as different map types and usage models by changing the options below."""
        ),
        html.Div(
            html.Label(["Drug Type:",
                dcc.Dropdown(
                    id='drugtype',
                    options=[
                        {'label': 'Cannabis', 'value': 'cannabis'}],
                    style={'width': '100%', 'display': 'block'},
                    value='cannabis')]),
            className="div-for-dropdown"),
        html.Div(
            html.Label(["Map Type:",
                dcc.RadioItems(
                    id='maptype',
                    options=[
                        {'label': 'Log', 'value': 'standard'},
                        {'label': 'Quantiles', 'value': 'quantiles'},
                        {'label': '95% Confidence', 'value': 'confidence'},
                    ],
                    labelStyle={'display': 'inline-block', "padding-right": "10px"},
                    style={'width': '100%', 'display': 'block', "margin-right": "10px"},
                    value='standard',
                    )]),
            className="div-for-dropdown"),
        html.Div(
            html.Label(["CI Type:",
                dcc.RadioItems(
                    id='citype',
                    options=[
                        {'label': 'Wilson Interval', 'value': 'wilson'},
                    ],
                    style={'width': '100%', 'display': 'block'},
                    value='wilson',
                    )]),
            className="div-for-dropdown"),
        html.Div(
            html.Label(["Usage Model:",
                dcc.RadioItems(
                    id='usagemodel',
                    options=[
                        {'label': 'Age, Race, Sex', 'value': 'normal'},
                        {'label': 'Age, Race, Sex, Poverty Status', 'value': 'poverty'},
                        {'label': 'Age, Race, Sex, Urban Area', 'value': 'urban'},
                    ],
                    style={'width': '100%', 'display': 'block'},
                    value='normal',
                    )]),
            className="div-for-dropdown"),
        html.Div(
            html.Label(["Republican Vote Share (2020):", 
                dcc.Checklist(
                    id="republican-boxes",
                    options=[
                        {'label': '<20%', 'value': '<20%'},
                        {'label': '20-40%', 'value': '20-40%'},
                        {'label': '40-60%', 'value': '40-60%'},
                        {'label': '60-80%', 'value': '60-80%'},
                        {'label': '80-100%', 'value': '80-100%'},
                    ],
                    value=['<20%', '20-40%', '40-60%', '60-80%', '80-100%'],
                    labelStyle={'display': 'inline-block', "padding-right": "10px"}
                    )]), 
            className="div-for-dropdown"),
        dcc.Markdown(
            """
            Source: NIBRS Drug Incidient Bias - Link to paper to be added.
            
            Links: [Source Code](https://github.com/predictive-analytics-lab/drug-map) | [Twitter] (https://twitter.com/WeArePal_ai)
            """
        )])

smoothing_ui = html.Div(className="",
    children=[
        dcc.RadioItems(id='maptype', value="standard", style = dict(display='none')),
        dcc.RadioItems(id='usagemodel', value="normal", style = dict(display='none')),
        dcc.RadioItems(id='citype', value="none", style = dict(display='none')),
        html.H2("USA DRUG BIAS MAP"),
        html.P(
            """Select different drugs, as well as different map types and usage models by changing the options below."""
        ),
        html.Div(
            html.Label(["Drug Type:",
                dcc.Dropdown(
                    id='drugtype',
                    options=[
                        {'label': 'Cannabis', 'value': 'cannabis'}],
                    style={'width': '100%', 'display': 'block'},
                    value='cannabis')]),
            className="div-for-dropdown"),
        html.Div(
            html.Label(["Map Type:",
                dcc.RadioItems(
                    id='maptype',
                    options=[
                        {'label': 'Log', 'value': 'standard'},
                        {'label': 'Quantiles', 'value': 'quantiles'},
                        {'label': '95% Confidence', 'value': 'confidence'},
                    ],
                    labelStyle={'display': 'inline-block', "padding-right": "10px"},
                    style={'width': '100%', 'display': 'block', "margin-right": "10px"},
                    value='standard',
                    )]),
            className="div-for-dropdown"),
        html.Div(
            html.Label(["CI Type:",
                dcc.RadioItems(
                    id='citype',
                    options=[
                        {'label': 'Wilson Interval', 'value': 'wilson'},
                    ],
                    style={'width': '100%', 'display': 'block'},
                    value='wilson',
                    )]),
            className="div-for-dropdown"),
        html.Div(
            html.Label(["Urban Filter:",      
                dcc.Slider(
                    id='urbanfilter',
                    min=2,
                    max=3,
                    value=2,
                    marks={m: str(m) for m in range(2, 4)}
                )]),
            className="div-for-dropdown"),
        html.Div([
            html.P("""
                         Current smoothing function is a simple average weighted by the distance from surrounding counties.
                         
                         Where the weights are:
                         
                            1 / (d + 1) ** p
                         
                         Where d is the distance between the smoothing point and the county, and p is the power of the distance that can be controlled with the slider below:
                         """),
            html.Label(["Smoothing Power:",      
                dcc.Slider(
                    id='smoothingparameter',
                    min=1,
                    max=2,
                    step=None,
                    value=1,
                    marks={m: str(m) for m in [1, 1.5, 2]}
                )])],
            className="div-for-dropdown"),
        html.Div(
            html.Label(["Republican Vote Share (2020):", 
                dcc.Checklist(
                    id="republican-boxes",
                    options=[
                        {'label': '<20%', 'value': '<20%'},
                        {'label': '20-40%', 'value': '20-40%'},
                        {'label': '40-60%', 'value': '40-60%'},
                        {'label': '60-80%', 'value': '60-80%'},
                        {'label': '80-100%', 'value': '80-100%'},
                    ],
                    value=['<20%', '20-40%', '40-60%', '60-80%', '80-100%'],
                    labelStyle={'display': 'inline-block', "padding-right": "10px"}
                    )]), 
            className="div-for-dropdown"),
        dcc.Markdown(
            """
            Source: NIBRS Drug Incidient Bias - Link to paper to be added.
            
            Links: [Source Code](https://github.com/predictive-analytics-lab/drug-map) | [Twitter] (https://twitter.com/WeArePal_ai)
            """
        )])

drug_map = dcc.Graph(id="drug-map", style={"height":"85vh"})
smoothed_map = dcc.Graph(id="smoothed-map", style={"height":"85vh"})


tab_style = {
    "background-color": "#31302F",
    "color": "#d8d8d8",
    "border-color": "#31302F",
    "font-size": "1.2em",
}

selected_tab_style = {
    "background-color": "#31302F",
    "color": "#FFFFFF",
    "border": "0",
    "font-size": "1.2em",
    "box-shadow": "0 0 15px 0px #000",
    "clip-path": "inset(0px -15px 0px -15px)"
}

app.layout = html.Div(
    children=[
        dcc.Store(id='clientside-data-store'),
        html.Div(
            id="ui-div",
            className="three columns div-user-controls",
            children=[base_ui],
        ),
        html.Div(
            className="nine columns div-for-charts bg-grey",
            children=[
                dcc.Tabs(id="tabs", value='standard', children=[
                    dcc.Tab(id="standard_tab", className="custom-tab", label='Standard Map', style=tab_style, selected_style=selected_tab_style, value="standard", children=[drug_map]),
                    dcc.Tab(id="smoothed_tab", className="custom-tab", label='Smoothed Map', style=tab_style, selected_style=selected_tab_style, value="smoothed", children=[smoothed_map])
                ]),
                dcc.Slider(
                    id='time-slider',
                    min=2012,
                    max=2019,
                    step=1,
                    value=2019,
                    marks={year: str(year) for year in range(2012, 2020)})
            ]
        )
    ]
)

@app.callback([Output('ui-div', 'children'), Output('standard_tab', 'children'), Output('smoothed_tab', 'children')], [Input('tabs', 'value')])
def update_ui(tabs: str) -> list:
    if tabs == "standard":
        return [base_ui], [drug_map], [smoothed_map]
    else:
        return [smoothing_ui], [drug_map], [smoothed_map]

@app.callback(
    [
        Output('clientside-data-store','data')
    ],
    [
        Input('drugtype','value'),
        Input('usagemodel','value'),
        Input('citype','value'),
        Input('time-slider','value'),
        Input('republican-boxes','value'),
        Input('urbanfilter','value'),
        Input('smoothingparameter', 'value')
    ],
    [
        State('tabs', 'value')
    ])
@cache.memoize(timeout=timeout)
def update_data(drugtype: str, model: str, citype: str, time: int, republican: List[str], urban_filter: int, smoothing_parameter: str, tab: str) -> dict:
    df = mapping.args_to_df(drug_type=drugtype, smoothed=tab=="smoothed", year=time, citype=citype, model=model, republican_cats=republican, urban_filter=str(urban_filter), smoothing_param=float(smoothing_parameter))
    df_dict = df.reset_index().to_dict(orient='list')
    return [df_dict]

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='get_map'
    ),
    Output('drug-map', 'figure'),
    Output('smoothed-map', 'figure'),
    Input('clientside-data-store', 'data'),
    Input('maptype', 'value'),
    State('tabs', 'value')
)