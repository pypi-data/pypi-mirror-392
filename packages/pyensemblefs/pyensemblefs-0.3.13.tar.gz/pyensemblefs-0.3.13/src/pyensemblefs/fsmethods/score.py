from __future__ import annotations
from typing import Optional, Union
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator
from .basefs import FSMethod


try:
    from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
except Exception:
    mutual_info_classif = None
    mutual_info_regression = None

try:
    from scipy.stats import pearsonr, spearmanr
except Exception:
    pearsonr = None
    spearmanr = None

try:
    from sklearn.neighbors import kneighbors_graph
except Exception:
    kneighbors_graph = None


class FisherScore(FSMethod, BaseEstimator):
    """Fisher score for classification: ratio of between-class to within-class variance, per feature."""

    def __init__(self, name: str = None, target_type: str = "classification"):
        super().__init__(name=name or "FisherScore", target_type=target_type)

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> "FisherScore":
        X, y = self._check_input(X, y)
        if self.target_type != "classification":
            raise ValueError("FisherScore is defined for classification targets.")
        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)
        y_np = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else np.asarray(y)

        classes = np.unique(y_np)
        if classes.size < 2:
            raise ValueError("FisherScore needs at least two classes.")

        n_features = X_np.shape[1]
        scores = np.zeros(n_features, dtype=float)

        for j in range(n_features):
            mu_j = X_np[:, j].mean()
            num = 0.0
            den = 0.0
            for c in classes:
                Xc = X_np[y_np == c, j]
                n_c = Xc.size
                mu_c = Xc.mean()
                var_c = Xc.var(ddof=1) if n_c > 1 else 0.0
                num += n_c * (mu_c - mu_j) ** 2
                den += n_c * var_c
            scores[j] = num / (den + 1e-12)

        self.feature_importances_ = scores
        self._post_fit()
        return self


class MIScore(FSMethod, BaseEstimator):
    """Mutual Information score per feature (classification or regression)."""

    def __init__(self, target_type: str = "classification", discrete_features: Union[bool, str] = "auto",
                 n_neighbors: int = 3, name: str = None, random_state: Optional[int] = None):
        super().__init__(name=name or "MIScore", target_type=target_type)
        self.discrete_features = discrete_features
        self.n_neighbors = n_neighbors
        self.random_state = random_state

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> "MIScore":
        X, y = self._check_input(X, y)

        if mutual_info_classif is None:
            raise ImportError("scikit-learn mutual_info_* is required for MIScore.")

        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)
        y_np = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else np.asarray(y)

        if self.target_type == "classification":
            mi = mutual_info_classif(
                X_np, y_np,
                discrete_features=self.discrete_features,
                n_neighbors=self.n_neighbors,
                random_state=self.random_state
            )
        elif self.target_type == "regression":
            mi = mutual_info_regression(
                X_np, y_np,
                discrete_features=self.discrete_features,
                n_neighbors=self.n_neighbors,
                random_state=self.random_state
            )
        else:
            raise ValueError("MIScore target_type must be 'classification' or 'regression'.")

        self.feature_importances_ = np.asarray(mi, dtype=float)
        self._post_fit()
        return self


class CorrelationScore(FSMethod, BaseEstimator):
    """Absolute correlation score per feature with target (Pearson or Spearman)."""

    def __init__(self, method: str = "pearson", name: str = None, target_type: str = "regression"):
        super().__init__(name=name or f"CorrelationScore[{method}]", target_type=target_type)
        self.method = method

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> "CorrelationScore":
        X, y = self._check_input(X, y)

        if self.method not in ("pearson", "spearman"):
            raise ValueError("method must be 'pearson' or 'spearman'.")

        if (self.method == "pearson" and pearsonr is None) or (self.method == "spearman" and spearmanr is None):
            raise ImportError("scipy.stats (pearsonr/spearmanr) is required for CorrelationScore.")

        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)
        y_np = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else np.asarray(y)

        n_features = X_np.shape[1]
        scores = np.zeros(n_features, dtype=float)

        for j in range(n_features):
            xj = X_np[:, j]
            if self.method == "pearson":
                r, _ = pearsonr(xj, y_np)
            else:
                r, _ = spearmanr(xj, y_np)
            if np.isnan(r):
                r = 0.0
            scores[j] = abs(r)

        self.feature_importances_ = scores
        self._post_fit()
        return self


class LaplacianScore(FSMethod, BaseEstimator):
    """
    Unsupervised Laplacian Score (He et al., 2005):
    Features that are smoother on the data manifold (graph) get lower scores.
    We invert to return higher-is-better scores via `score = 1 / (lap_score + eps)`.

    Parameters
    ----------
    n_neighbors : int
        k for k-NN graph.
    mode : {"knn"}
        Graph construction mode (currently only "knn").
    eps : float
        Small constant to avoid division by zero.
    """

    def __init__(self, n_neighbors: int = 5, mode: str = "knn", eps: float = 1e-12, name: str = None):
        super().__init__(name=name or "LaplacianScore", target_type="unsupervised")
        self.n_neighbors = n_neighbors
        self.mode = mode
        self.eps = eps

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y=None) -> "LaplacianScore":
        X, _ = self._check_input(X, np.zeros(len(X)))
        if kneighbors_graph is None:
            raise ImportError("scikit-learn kneighbors_graph is required for LaplacianScore.")
        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)

        W = kneighbors_graph(X_np, n_neighbors=self.n_neighbors, mode="connectivity", include_self=False)
        W = 0.5 * (W + W.T)

        d = np.asarray(W.sum(axis=1)).ravel()
        D = np.diag(d)
        L = D - W.toarray()

        scores = np.zeros(X_np.shape[1], dtype=float)
        for j in range(X_np.shape[1]):
            f = X_np[:, j]
            f = f - (d @ f) / (d.sum() + self.eps)  
            num = f.T @ L @ f
            den = f.T @ D @ f + self.eps
            lap = num / den
            scores[j] = 1.0 / (lap + self.eps)  # higher is better

        self.feature_importances_ = scores
        self._post_fit()
        return self


class HSICScore(FSMethod, BaseEstimator):
    """
    HSIC (Hilbert–Schmidt Independence Criterion) score per feature using RBF kernels.
    Higher HSIC implies stronger dependence with the target.

    Parameters
    ----------
    sigma_x : {"auto"} or float
        Bandwidth for feature kernel.
    sigma_y : {"auto"} or float
        Bandwidth for target kernel (y is reshaped to (n,1) if continuous).
    normalize : bool
        If True, return a normalized HSIC proxy in [approx] comparable scale.
    """

    def __init__(self, sigma_x: Union[str, float] = "auto",
                 sigma_y: Union[str, float] = "auto",
                 normalize: bool = True,
                 name: str = None,
                 target_type: str = "classification"):
        super().__init__(name=name or "HSICScore", target_type=target_type)
        self.sigma_x = sigma_x
        self.sigma_y = sigma_y
        self.normalize = normalize

    @staticmethod
    def _rbf_kernel(vec: np.ndarray, sigma: float) -> np.ndarray:
        v = vec.reshape(-1, 1)
        d2 = (v - v.T) ** 2
        return np.exp(-d2 / (2 * sigma ** 2 + 1e-12))

    @staticmethod
    def _median_heuristic(vec: np.ndarray) -> float:
        v = vec.reshape(-1, 1)
        dists = np.abs(v - v.T).ravel()
        med = np.median(dists[dists > 0]) if np.any(dists > 0) else 1.0
        return med if med > 0 else 1.0

    @staticmethod
    def _center(K: np.ndarray) -> np.ndarray:
        n = K.shape[0]
        H = np.eye(n) - np.ones((n, n)) / n
        return H @ K @ H

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> "HSICScore":
        X, y = self._check_input(X, y)
        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)
        y_np = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else np.asarray(y)

        if self.target_type == "classification":
            Ky = (y_np.reshape(-1, 1) == y_np.reshape(1, -1)).astype(float)
            Ky = self._center(Ky)
            normy = np.sqrt(np.trace(Ky @ Ky)) + 1e-12
        else:
            sigy = self._median_heuristic(y_np) if self.sigma_y == "auto" else float(self.sigma_y)
            Ky = self._rbf_kernel(y_np, sigy)
            Ky = self._center(Ky)
            normy = np.sqrt(np.trace(Ky @ Ky)) + 1e-12

        scores = np.zeros(X_np.shape[1], dtype=float)
        for j in range(X_np.shape[1]):
            xj = X_np[:, j]
            sigx = self._median_heuristic(xj) if self.sigma_x == "auto" else float(self.sigma_x)
            Kx = self._rbf_kernel(xj, sigx)
            Kx = self._center(Kx)
            if self.normalize:
                num = np.trace(Kx @ Ky)
                normx = np.sqrt(np.trace(Kx @ Kx)) + 1e-12
                scores[j] = num / (normx * normy)
            else:
                scores[j] = np.trace(Kx @ Ky)

        self.feature_importances_ = scores
        self._post_fit()
        return self