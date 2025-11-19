from __future__ import annotations
import pandas as pd
from sklearn.datasets import load_breast_cancer

def load_breast_cancer_dataset(as_frame: bool = True) -> pd.DataFrame:
    ds = load_breast_cancer(as_frame=True)
    X, y = ds.data, ds.target
    df = pd.concat([X, y.rename("target")], axis=1)
    return df if as_frame else df.values
