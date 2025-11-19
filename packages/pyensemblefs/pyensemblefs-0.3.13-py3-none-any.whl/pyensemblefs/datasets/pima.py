from __future__ import annotations
import pandas as pd
from sklearn.datasets import fetch_openml

def load_pima_dataset(as_frame: bool = True) -> pd.DataFrame:
    """
    Pima Indians Diabetes (OpenML 'diabetes', id=37). Returns a DataFrame with
    features + 'target' column (binary).
    """
    data = fetch_openml(name="diabetes", version=1, as_frame=True)
    X, y = data.data.copy(), data.target.copy()
    # normalizar nombre de target
    if "class" in y.name.lower():
        y.name = "target"
    df = pd.concat([X, y.rename("target")], axis=1)
    return df if as_frame else df.values
