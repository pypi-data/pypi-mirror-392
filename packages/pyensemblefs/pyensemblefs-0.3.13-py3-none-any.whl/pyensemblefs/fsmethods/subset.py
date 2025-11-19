from __future__ import annotations
from typing import Optional, Union, Literal
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.preprocessing import KBinsDiscretizer
from .basefs import FSMethod

try:
    from sklearn.feature_selection import mutual_info_classif
except Exception:
    mutual_info_classif = None


class SubsetFilter(FSMethod, BaseEstimator):

    def __init__(self, rule: str = "variance", k: Optional[int] = None,
                 threshold: Optional[float] = None, name: Optional[str] = None,
                 target_type: Optional[str] = None):
        super().__init__(name=name or f"SubsetFilter[{rule}]", target_type=target_type)
        self.rule = rule
        self.k = k
        self.threshold = threshold

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Optional[Union[pd.Series, np.ndarray]] = None) -> "SubsetFilter":
        X, y = self._check_input(X, y if y is not None else np.zeros(len(X)))
        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)

        if self.rule == "variance":
            scores = np.nan_to_num(np.var(X_np, axis=0), nan=0.0)
            if self.k is not None:
                idx = np.argsort(-scores)[: self.k]
                mask = np.zeros(X_np.shape[1], dtype=int)
                mask[idx] = 1
            else:
                thr = self.threshold if self.threshold is not None else 0.0
                mask = (scores > thr).astype(int)
        else:
            raise ValueError(f"Unknown rule '{self.rule}'")

        self.feature_importances_ = scores
        self.selected_features_ = mask

        order = np.argsort(-scores)
        ranks = np.empty_like(order)
        ranks[order] = np.arange(1, X_np.shape[1] + 1)
        self.ranking_ = ranks

        self._post_fit()
        return self



class MRMRSubset(FSMethod, BaseEstimator):

    def __init__(self, k: int, redundancy: Literal["mi", "corr"] = "mi",
                 discrete_features: Union[bool, str] = "auto",
                 n_bins: int = 5,
                 name: Optional[str] = None,
                 target_type: str = "classification"):
        super().__init__(name=name or f"MRMRSubset[{redundancy}]", target_type=target_type)
        self.k = int(k)
        self.redundancy = redundancy
        self.discrete_features = discrete_features
        self.n_bins = n_bins

    @staticmethod
    def _abs_corr(X: np.ndarray) -> np.ndarray:
        C = np.corrcoef(X, rowvar=False)
        return np.abs(C)

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> "MRMRSubset":
        if self.k <= 0:
            raise ValueError("k must be positive.")

        X, y = self._check_input(X, y)
        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)
        y_np = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else np.asarray(y)
        n, p = X_np.shape

        if mutual_info_classif is None:
            raise ImportError("scikit-learn mutual_info_classif is required for mRMR relevance.")

        rel = mutual_info_classif(X_np, y_np, discrete_features=self.discrete_features)
        rel = np.asarray(rel, dtype=float)

        if self.redundancy == "mi":
            Red = self._abs_corr(X_np)
        elif self.redundancy == "corr":
            Red = self._abs_corr(X_np)
        else:
            raise ValueError("redundancy must be 'mi' or 'corr'.")

        selected = []
        available = set(range(p))

        j0 = int(np.argmax(rel))
        selected.append(j0)
        available.remove(j0)

        while len(selected) < self.k and available:
            best_j = None
            best_score = -np.inf
            for j in list(available):
                if selected:
                    red = np.mean([Red[j, s] for s in selected])
                else:
                    red = 0.0
                score = rel[j] - red
                if score > best_score:
                    best_score = score
                    best_j = j
            selected.append(best_j)
            available.remove(best_j)

        mask = np.zeros(p, dtype=int)
        mask[selected] = 1
        self.selected_features_ = mask

        ranks = np.empty(p, dtype=int)
        ranks[:] = p + 1 
        for r, j in enumerate(selected, start=1):
            ranks[j] = r
        self.ranking_ = ranks

        fi = np.zeros(p, dtype=float)
        for j in range(p):
            if mask[j]:
                S = [s for s in selected if s != j]
                red = np.mean([Red[j, s] for s in S]) if S else 0.0
                fi[j] = rel[j] - red
            else:
                fi[j] = 0.0
        self.feature_importances_ = fi

        self._post_fit()
        return self



class CFSSubset(FSMethod, BaseEstimator):

    def __init__(self, k: int, name: Optional[str] = None, target_type: str = "classification"):
        super().__init__(name=name or "CFSSubset", target_type=target_type)
        self.k = int(k)

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> "CFSSubset":
        if self.k <= 0:
            raise ValueError("k must be positive.")
        X, y = self._check_input(X, y)
        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)
        y_np = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else np.asarray(y)

        p = X_np.shape[1]
        r_xy = np.array([abs(np.corrcoef(X_np[:, j], y_np)[0, 1]) for j in range(p)])
        r_xx = np.abs(np.corrcoef(X_np, rowvar=False))

        selected = []
        available = set(range(p))

        def merit(S):
            if not S:
                return 0.0
            k = len(S)
            rel = np.mean(r_xy[S])
            if k == 1:
                red = 0.0
            else:
                sub = r_xx[np.ix_(S, S)]
                red = (np.sum(sub) - np.sum(np.diag(sub))) / (k * (k - 1))
            return (k * rel) / np.sqrt(k + k * (k - 1) * red + 1e-12)

        while len(selected) < self.k and available:
            best, best_merit = None, -np.inf
            for j in list(available):
                cand = selected + [j]
                m = merit(cand)
                if m > best_merit:
                    best, best_merit = j, m
            selected.append(best)
            available.remove(best)

        mask = np.zeros(p, dtype=int)
        mask[selected] = 1
        self.selected_features_ = mask

        ranks = np.empty(p, dtype=int)
        ranks[:] = p + 1
        for r, j in enumerate(selected, start=1):
            ranks[j] = r
        self.ranking_ = ranks
        self.feature_importances_ = r_xy 
        self._post_fit()
        return self



def _entropy_discrete(vec: np.ndarray) -> float:
    vals, cnts = np.unique(vec, return_counts=True)
    p = cnts.astype(float) / cnts.sum()
    return -np.sum(p * np.log2(p + 1e-12))


def _joint_entropy(xd: np.ndarray, yd: np.ndarray) -> float:
    x_vals, x_inv = np.unique(xd, return_inverse=True)
    y_vals, y_inv = np.unique(yd, return_inverse=True)
    J = np.zeros((x_vals.size, y_vals.size), dtype=float)
    np.add.at(J, (x_inv, y_inv), 1.0)
    p = J / J.sum()
    return -np.sum(p[p > 0] * np.log2(p[p > 0]))


def _symmetrical_uncertainty(xd: np.ndarray, yd: np.ndarray) -> float:
    hx = _entropy_discrete(xd)
    hy = _entropy_discrete(yd)
    hxy = _joint_entropy(xd, yd)
    num = 2.0 * (hx + hy - hxy)
    den = (hx + hy + 1e-12)
    return num / den


class FCBFSubset(FSMethod, BaseEstimator):


    def __init__(self, delta: float = 0.05, n_bins: int = 5, k: Optional[int] = None,
                 name: Optional[str] = None, target_type: str = "classification"):
        super().__init__(name=name or "FCBFSubset", target_type=target_type)
        self.delta = float(delta)
        self.n_bins = int(n_bins)
        self.k = k

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> "FCBFSubset":

        self.selected_features_ = None
        self.ranking_ = None
        self.feature_importances_ = None

        X, y = self._check_input(X, y)
        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)
        y_np = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else np.asarray(y)

        try:
            kbd = KBinsDiscretizer(n_bins=self.n_bins, encode="ordinal", strategy="quantile", quantile_method="averaged_inverted_cdf")
            Xd = kbd.fit_transform(X_np)
            if hasattr(Xd, "toarray"):
                Xd = Xd.toarray()
            Xd = Xd.astype(int, copy=False)
            yd = y_np.astype(int, copy=False)

            p = Xd.shape[1]

            if p == 0:
                self.selected_features_ = np.zeros(0, dtype=int)
                self.ranking_ = np.zeros(0, dtype=int)
                self.feature_importances_ = np.zeros(0, dtype=float)
                self._post_fit()
                return self

            su_y = np.zeros(p, dtype=float)
            for j in range(p):
                su = _symmetrical_uncertainty(Xd[:, j], yd)
                su_y[j] = 0.0 if not np.isfinite(su) else su

            R = [j for j in range(p) if su_y[j] >= float(self.delta)]
            R.sort(key=lambda j: su_y[j], reverse=True)

            selected = []
            for i in R:
                drop = False
                for j in selected:
                    su_ij = _symmetrical_uncertainty(Xd[:, i], Xd[:, j])
                    if not np.isfinite(su_ij):
                        su_ij = 0.0
                    if su_y[i] <= su_ij:
                        drop = True
                        break
                if not drop:
                    selected.append(i)

            if self.k is not None and len(selected) > self.k:
                selected = selected[: int(self.k)]

            mask = np.zeros(p, dtype=int)
            if len(selected) > 0:
                mask[selected] = 1
            self.selected_features_ = mask

            order = np.argsort(-su_y)
            ranks = np.empty(p, dtype=int)
            ranks[order] = np.arange(1, p + 1)
            self.ranking_ = ranks

            self.feature_importances_ = su_y

        finally:
            if self.selected_features_ is None:
                p = X_np.shape[1]
                self.selected_features_ = np.zeros(p, dtype=int)
            if self.ranking_ is None:
                p = X_np.shape[1]
                self.ranking_ = np.arange(1, p + 1, dtype=int)  # arbitrary order
            if self.feature_importances_ is None:
                p = X_np.shape[1]
                self.feature_importances_ = np.zeros(p, dtype=float)

            self._post_fit()

        return self