import pandas as pd
import plotly as py
import plotly.express as px
import numpy as np

from pathlib import Path
from urllib.request import urlopen
import json

data_path = Path(__file__).parent.parent / "data"

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
    
def args_to_map(drug_type: str = "cannabis", smoothed: bool = False, map_type: str = "standard") -> py.graph_objs.Figure:
    df = args_to_df(drug_type=drug_type, smoothed=smoothed)
    if map_type == "confidence":
        return confidence_map(df)
    elif map_type == "standard":
        return map_with_slider(df)
    else:
        pass   

def args_to_df(drug_type: str = "cannabis", smoothed: bool = False) -> pd.DataFrame:
    smoothed_str = "smoothed" if smoothed else "unsmoothed"
    filename = f"{drug_type}_{smoothed_str}.csv"
    return pd.read_csv(str(data_path / filename), dtype={"FIPS": str})

def confidence_map(df: pd.DataFrame, time_col: str = "year"):
    
    color_map = {"S>5":"#E76258",
                 "S>2":"#EAB055",
                 "S>1":"#E0D987",
                 "S<1":"#5E925F",
                 "S<0.5":"#265F47",
                 "S<0.2":"#52675B",
                 "S~1":"#689891"}

    fig = px.choropleth_mapbox(
        df, 
        geojson=counties,
        locations='FIPS', 
        color="cat",
        color_discrete_map=color_map,
        mapbox_style="carto-positron",
        opacity=0.5,
        center = {'lat': 41.567243, 'lon': -101.271556},
        hover_data=["slci", "cat", "incidents", "frequency", "urban_code", "bwratio"],
        labels={
            "year": "Year",
            "cat": '95% Confidence S>X',
            "slci": 'Selection Ratios by Race (Black/White) with CIs',
            'incidents': "Number of recorded Incidents",
            "bwratio": "Black / White Ratio",
            "urban_code": "Urban Code",
            "frequency": "Population"},
        zoom=3.7,
        animation_frame=time_col
    )
    fig.update_geos(fitbounds="locations",visible=False, scope="usa")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},)
    return fig

def map_with_slider(df: pd.DataFrame, time_col: str = "year", log: bool = True,):

    fig = px.choropleth_mapbox(
        df, 
        geojson=counties,
        locations='FIPS', 
        color="selection_ratio_log10",
        color_continuous_scale="Viridis",
        range_color=(-2, 2),
        mapbox_style="carto-positron",
        opacity=0.5,
        center = {'lat': 39.567243, 'lon': -101.271556},
        hover_data=["slci", "incidents", "frequency", "urban_code", "bwratio"],
        labels={
            "year": "Year",
            "slci": 'Selection Ratios by Race (Black/White) with CIs',
            'incidents': "Number of recorded Incidents",
            "bwratio": "Black / White Ratio",
            "urban_code": "Urban Code",
            "frequency": "Population"},
        zoom=3.7,
        animation_frame=time_col
    )
    fig.update_geos(fitbounds="locations",visible=False, scope="usa")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},)
    return fig