from __future__ import annotations
import pandas as pd
from sklearn.datasets import load_diabetes

def load_sklearn_diabetes_dataset(as_frame: bool = True) -> pd.DataFrame:
    """
    Sklearn diabetes (regresión). Devuelve 'target' como continuo.
    """
    ds = load_diabetes(as_frame=True)
    X, y = ds.data, ds.target
    df = pd.concat([X, y.rename("target")], axis=1)
    return df if as_frame else df.values
