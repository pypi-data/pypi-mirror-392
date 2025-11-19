from __future__ import annotations
import numpy as np
from typing import Optional
from .base import BaseSelector
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

try:
    from skrebate import ReliefF as _ReliefF
    _HAS_SKREBATE = True
except Exception:
    _HAS_SKREBATE = False
    _ReliefF = None  # type: ignore

from sklearn.base import BaseEstimator


class ReliefSelector(BaseEstimator):
    """
    Thin wrapper around scikit-rebate's ReliefF:
    - fit(X, y) sets feature_importances_
    - get_support(indices=False) selects top-k (if k is provided)
    Compatible with Bootstrapper/MetaBootstrapper contracts.
    """
    def __init__(self, n_neighbors: int = 100, k: Optional[int] = None,
                 random_state: Optional[int] = None, **kwargs):
        if not _HAS_SKREBATE:
            raise ImportError(
                "ReliefSelector requires 'scikit-rebate'. "
                "Install extra: pip install 'pyensemblefs[relief]'"
            )
        self.n_neighbors = int(n_neighbors)
        self.k = None if k is None else int(k)
        self.random_state = random_state
        self.kwargs = dict(kwargs)
        self.feature_importances_ = None
        self._n_features_ = None

    def fit(self, X, y):
        if hasattr(X, "values"):
            X_arr = X.values
        else:
            X_arr = np.asarray(X)
        y_arr = np.asarray(y).ravel()
        rf = _ReliefF(n_neighbors=self.n_neighbors, n_jobs=1, **self.kwargs)
        rf.fit(X_arr, y_arr)
        self.feature_importances_ = np.asarray(rf.feature_importances_, dtype=float).ravel()
        self._n_features_ = int(self.feature_importances_.shape[0])
        return self

    def get_support(self, indices: bool = False):
        if self.feature_importances_ is None or self._n_features_ is None:
            raise RuntimeError("Call fit() before get_support().")
        p = self._n_features_
        if self.k is None or self.k >= p:
            return np.arange(p) if indices else np.ones(p, dtype=bool)
        order = np.argsort(-self.feature_importances_)
        idx = order[: self.k]
        if indices:
            return idx
        mask = np.zeros(p, dtype=bool)
        mask[idx] = True
        return mask
    

class RandomForestSelector(BaseSelector):
    def __init__(self, k: Optional[int] = None, n_estimators: int = 300, random_state: int = 42):
        super().__init__(k=k, name="RFSelector")
        self.n_estimators = n_estimators
        self.random_state = random_state

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestSelector":
        X = np.asarray(X); y = np.asarray(y)
        rf = RandomForestClassifier(n_estimators=self.n_estimators, random_state=self.random_state, n_jobs=-1)
        rf.fit(X, y)
        scores = np.nan_to_num(rf.feature_importances_, nan=0.0)

        order = np.argsort(-scores)
        ranks = np.empty_like(order); ranks[order] = np.arange(1, X.shape[1] + 1)

        mask = np.zeros(X.shape[1], dtype=int)
        if self.k is not None:
            mask[order[: self.k]] = 1

        self.feature_importances_ = scores
        self.ranking_ = ranks
        self.selected_features_ = mask
        self._ensure_outputs(X.shape[1])
        return self


class L1LogisticSelector(BaseSelector):
    def __init__(self, k: Optional[int] = None, C: float = 1.0, max_iter: int = 2000, random_state: int = 42):
        super().__init__(k=k, name="L1LogReg")
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state

    def fit(self, X: np.ndarray, y: np.ndarray) -> "L1LogisticSelector":
        X = np.asarray(X); y = np.asarray(y)
        lr = LogisticRegression(penalty="l1", C=self.C, solver="liblinear",
                                random_state=self.random_state, max_iter=self.max_iter)
        lr.fit(X, y)
        coef = np.abs(lr.coef_).ravel()
        scores = np.nan_to_num(coef, nan=0.0)

        order = np.argsort(-scores)
        ranks = np.empty_like(order); ranks[order] = np.arange(1, X.shape[1] + 1)

        mask = np.zeros(X.shape[1], dtype=int)
        if self.k is not None:
            mask[order[: self.k]] = 1

        self.feature_importances_ = scores
        self.ranking_ = ranks
        self.selected_features_ = mask
        self._ensure_outputs(X.shape[1])
        return self
