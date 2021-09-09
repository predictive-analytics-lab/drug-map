import pandas as pd
import plotly as py
import plotly.express as px
import numpy as np

from pathlib import Path
from urllib.request import urlopen
import json

data_path = Path(__file__).parent.parent / "data"

def load_df():
    dfs = {}
    for file in data_path.iterdir():
        dfs[file.name] = pd.read_csv(str(data_path / file), dtype={"FIPS": str})
    return dfs

data_dict = load_df()

def args_to_df(drug_type: str,
               citype: str,
               model: str,
               smoothed: bool,
               year: int = 2019) -> pd.DataFrame:
    filename = f"selection_ratio_county_2012-2019_{citype}"
    if model == "poverty":
        filename += "_poverty"
    elif model == "urban":
        filename += "_urban"
    df = data_dict[filename + ".csv"]
    return df[df["year"] == year]