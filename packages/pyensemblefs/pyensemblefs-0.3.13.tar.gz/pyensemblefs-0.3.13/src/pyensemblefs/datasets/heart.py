from __future__ import annotations
import pandas as pd
from sklearn.datasets import fetch_openml

def load_heart_dataset(as_frame: bool = True) -> pd.DataFrame:
    """
    UCI Heart Disease via OpenML ('heart-disease', id=53).
    """
    data = fetch_openml(name="heart-disease", version=1, as_frame=True)
    X, y = data.data.copy(), data.target.copy()
    y = (y.astype(str).str.lower().isin(["present","1","yes","true"])).astype(int)
    df = pd.concat([X, y.rename("target")], axis=1)
    return df if as_frame else df.values
