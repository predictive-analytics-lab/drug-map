import pandas as pd
from pathlib import Path
import numpy as np

data_path = Path(__file__).parent.parent / "data"

def load_df():
    dfs = {}
    for file in data_path.iterdir():
        dfs[file.name] = pd.read_csv(str(data_path / file), dtype={"FIPS": str})
    return dfs

def confidence_categorization(df: pd.DataFrame, value_col: str, ci_col: str) -> pd.DataFrame:
    def _categorization(v, ci):
        if v - ci > 5:
            return "S>5"
        if v - ci > 2:
            return "S>2"
        if v - ci > 1:
            return "S>1"
        if v + ci < 1:
            return "S<1"
        if v + ci < 0.5:
            return "S<0.5"
        if v + ci < 0.2:
            return "S<0.2"
        return "Low confidence"
    df["cat"] = df.apply(lambda x: _categorization(x[value_col], x[ci_col]), axis=1)
    return df

def confidence_categorization_alt(df: pd.DataFrame, value_col: str, ub_col: str, lb_col: str) -> pd.DataFrame:
    def _categorization(v, lb, ub):
        if lb > 5:
            return "S>5"
        if lb > 2:
            return "S>2"
        if lb > 1:
            return "S>1"
        if ub < 1:
            return "S<1"
        if ub < 0.5:
            return "S<0.5"
        if ub < 0.2:
            return "S<0.2"
        return "Low confidence"
    df["cat"] = df.apply(lambda x: _categorization(x[value_col], x[lb_col], x[ub_col]), axis=1)
    return df

def additions(df: pd.DataFrame) -> pd.DataFrame:
    if "ci" in df.columns:
        df = confidence_categorization(df, "selection_ratio", "ci")
    else:
        df = confidence_categorization_alt(df, "selection_ratio", "ub", "lb")

    df["frequency"] = df["frequency"].apply(lambda x: f'{int(x):,}')
    df["bwratio"] = df["bwratio"].apply(lambda x: f'{x:.3f}')
    
    if "ci" in df.columns:
        df["slci"] = df["selection_ratio"].round(3).astype(str) + " ± " + df["ci"].round(3).astype(str)
    else:
        df["slci"] = df["selection_ratio"].round(3).astype(str) + "(" + df["lb"].round(3).astype(str) + " - " + df["ub"].round(3).astype(str) + ")"

    df["selection_ratio_log10"] = np.log10(df["selection_ratio"])

    return df

if __name__ == "__main__":
    for file in data_path.iterdir():
        df = additions(pd.read_csv(str(data_path / file), dtype={"FIPS": str}))
        df.to_csv(file, index=False)
