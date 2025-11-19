from __future__ import annotations
import numpy as np
from typing import Optional, Literal
from .base import BaseSelector

from sklearn.feature_selection import f_classif, mutual_info_classif
from scipy.stats import ttest_ind


class AnovaSelector(BaseSelector):
    def __init__(self, k: Optional[int] = None):
        super().__init__(k=k, name="ANOVA")

    def fit(self, X: np.ndarray, y: np.ndarray) -> "AnovaSelector":
        X = np.asarray(X); y = np.asarray(y)
        F, pvalues = f_classif(X, y)
        scores = np.nan_to_num(F, nan=0.0, posinf=0.0, neginf=0.0)

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


class MutualInfoSelector(BaseSelector):
    def __init__(self, k: Optional[int] = None, discrete_features: Literal["auto", True, False] = "auto"):
        super().__init__(k=k, name="MutualInfo")
        self.discrete_features = discrete_features

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MutualInfoSelector":
        X = np.asarray(X); y = np.asarray(y)
        mi = mutual_info_classif(X, y, discrete_features=self.discrete_features, random_state=42)
        scores = np.nan_to_num(mi, nan=0.0)

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


class FisherSelector(BaseSelector):
    def __init__(self, k: Optional[int] = None, eps: float = 1e-12):
        super().__init__(k=k, name="Fisher")
        self.eps = eps

    def fit(self, X: np.ndarray, y: np.ndarray) -> "FisherSelector":
        X = np.asarray(X); y = np.asarray(y)
        y = y.ravel().astype(int)
        if np.unique(y).size != 2:
            raise ValueError("FisherSelector requires binary target.")
        c0, c1 = np.unique(y)
        X0 = X[y == c0]; X1 = X[y == c1]
        mu0, mu1 = X0.mean(axis=0), X1.mean(axis=0)
        var0, var1 = X0.var(axis=0), X1.var(axis=0)
        scores = ((mu1 - mu0) ** 2) / (var1 + var0 + self.eps)
        scores = np.nan_to_num(scores, nan=0.0)

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


class VarianceSelector(BaseSelector):
    def __init__(self, k: Optional[int] = None, threshold: float = 0.0):
        super().__init__(k=k, name="Variance")
        self.threshold = float(threshold)

    def fit(self, X: np.ndarray, y: np.ndarray | None = None) -> "VarianceSelector":
        X = np.asarray(X)
        scores = np.var(X, axis=0)
        scores = np.nan_to_num(scores, nan=0.0)

        order = np.argsort(-scores)
        ranks = np.empty_like(order); ranks[order] = np.arange(1, X.shape[1] + 1)

        if self.k is not None:
            mask = np.zeros(X.shape[1], dtype=int)
            mask[order[: self.k]] = 1
        else:
            mask = (scores > self.threshold).astype(int)

        self.feature_importances_ = scores
        self.ranking_ = ranks
        self.selected_features_ = mask
        self._ensure_outputs(X.shape[1])
        return self