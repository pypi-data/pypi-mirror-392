from __future__ import annotations
import numpy as np
from typing import Optional, Sequence
from .base import ScoreAggregator


__all__ = [
    "MeanAggregator",
    "SumAggregator",
    "MedianAggregator",
    "TrimmedMeanAggregator",
    "WinsorizedMeanAggregator",
    "GeometricMeanAggregator",
    "RankProductAggregator",
    "WeightedScoreAggregator",
    "BordaFromScoresAggregator",
    "SelectionFrequencyAggregator",
]



def _ensure_2d_scores(results: np.ndarray) -> np.ndarray:
    """Validate and return a 2D float array (n_bootstraps, n_features)."""
    A = np.asarray(results)
    if A.ndim != 2:
        raise ValueError("results must be a 2D array (n_bootstraps, n_features).")
    return A


class MeanAggregator(ScoreAggregator):
    """Arithmetic mean of per-bootstrap scores (higher = better)."""

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        A = _ensure_2d_scores(results)
        return A.mean(axis=0)


class SumAggregator(ScoreAggregator):
    """Sum of per-bootstrap scores (higher = better)."""

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        A = _ensure_2d_scores(results)
        return A.sum(axis=0)


class MedianAggregator(ScoreAggregator):
    """Median of per-bootstrap scores (robust to outliers)."""

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        A = _ensure_2d_scores(results)
        return np.median(A, axis=0)



class TrimmedMeanAggregator(ScoreAggregator):
    """
    Alpha-trimmed mean across bootstraps: trims a fraction `alpha` on each tail
    before averaging. Useful to mitigate outliers at the bootstrap level.

    Parameters
    ----------
    alpha : float in [0, 0.5)
        Proportion to trim on each tail (e.g., 0.1 trims 10% lowest & 10% highest).
    """

    def __init__(self, alpha: float = 0.1, top_k: Optional[int] = None):
        super().__init__(top_k=top_k)
        if not (0.0 <= alpha < 0.5):
            raise ValueError("alpha must be in [0, 0.5).")
        self.alpha = float(alpha)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        A = _ensure_2d_scores(results)
        B, _ = A.shape
        lo = int(np.floor(self.alpha * B))
        hi = B - lo
        A_sorted = np.sort(A, axis=0)
        trimmed = A_sorted[lo:hi, :]
        return trimmed.mean(axis=0)


class WinsorizedMeanAggregator(ScoreAggregator):
    """
    Winsorized mean across bootstraps: clip extremes to alpha-quantiles
    before averaging.

    Parameters
    ----------
    alpha : float in [0, 0.5)
        Proportion to winsorize on each tail.
    """

    def __init__(self, alpha: float = 0.1, top_k: Optional[int] = None):
        super().__init__(top_k=top_k)
        if not (0.0 <= alpha < 0.5):
            raise ValueError("alpha must be in [0, 0.5).")
        self.alpha = float(alpha)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        A = _ensure_2d_scores(results).astype(float)
        lo = np.quantile(A, self.alpha, axis=0, method="nearest")
        hi = np.quantile(A, 1 - self.alpha, axis=0, method="nearest")
        A = np.maximum(A, lo)
        A = np.minimum(A, hi)
        return A.mean(axis=0)


class GeometricMeanAggregator(ScoreAggregator):
    """
    Geometric mean across bootstraps:
    exp( mean( log(max(scores, eps)) ) ), emphasizing consistent high scores.
    """

    def __init__(self, eps: float = 1e-12, top_k: Optional[int] = None):
        super().__init__(top_k=top_k)
        if eps <= 0:
            raise ValueError("eps must be > 0.")
        self.eps = float(eps)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        A = _ensure_2d_scores(results).astype(float)
        return np.exp(np.mean(np.log(np.maximum(A, self.eps)), axis=0))


class RankProductAggregator(ScoreAggregator):
    """
    Rank-product style aggregator for *scores*: compute the product in log-domain.
    Lower log-product indicates consistently high scores; we return the negative
    log-product so that higher is better for downstream selection.

    Returns
    -------
    np.ndarray
        -sum(log(max(scores, eps))) across bootstraps (higher = better).
    """

    def __init__(self, eps: float = 1e-12, top_k: Optional[int] = None):
        super().__init__(top_k=top_k)
        if eps <= 0:
            raise ValueError("eps must be > 0.")
        self.eps = float(eps)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        A = _ensure_2d_scores(results).astype(float)
        return -np.sum(np.log(np.maximum(A, self.eps)), axis=0)



class WeightedScoreAggregator(ScoreAggregator):
    """
    Weighted average of per-bootstrap scores.
    If `weights` is None, reduces to the arithmetic mean.

    Parameters
    ----------
    weights : array-like of shape (n_bootstraps,), optional
        Non-negative weights. They will be normalized to sum to 1.
    """

    def __init__(self, weights: Optional[Sequence[float]] = None, top_k: Optional[int] = None):
        super().__init__(top_k=top_k)
        self.weights = None if weights is None else np.asarray(weights, dtype=float)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        A = _ensure_2d_scores(results)
        if self.weights is None:
            return A.mean(axis=0)
        w = np.asarray(self.weights, dtype=float)
        if w.shape != (A.shape[0],):
            raise ValueError(f"weights length must match n_bootstraps ({A.shape[0]}).")
        if np.any(w < 0):
            raise ValueError("weights must be non-negative.")
        s = w.sum()
        if s <= 0:
            raise ValueError("sum(weights) must be > 0.")
        w = w / s
        return np.average(A, axis=0, weights=w)


class BordaFromScoresAggregator(ScoreAggregator):
    """
    Borda aggregation from per-bootstrap scores:
      (1) convert each bootstrap row to ranks (1 = best),
      (2) assign Borda points (n_features - rank),
      (3) sum points across bootstraps (higher = better).
    """

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        S = _ensure_2d_scores(results)
        n_boot, n_feat = S.shape
        ranks = np.argsort(np.argsort(-S, axis=1), axis=1) + 1
        points = n_feat - ranks
        return points.sum(axis=0).astype(float)


class SelectionFrequencyAggregator(ScoreAggregator):
    """
    Convert binary 0/1 supports into selection frequencies in [0, 1].
    Accepts boolean, {0,1} int/float; values are cast to {0,1}.
    Use this when the base FS method returns subsets (supports).
    """

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        R = np.asarray(results)
        if R.ndim != 2:
            raise ValueError("results must be a 2D array (n_bootstraps, n_features).")
        if R.dtype == bool:
            M = R.astype(int)
        else:
            uniq = np.unique(R)
            if np.all(np.isin(uniq, [0, 1])):
                M = R.astype(int)
            else:
                M_rounded = np.rint(R)
                if np.all(np.isin(np.unique(M_rounded), [0, 1]) and np.allclose(R, M_rounded, atol=1e-8)):
                    M = M_rounded.astype(int)
                else:
                    raise ValueError("SelectionFrequencyAggregator expects binary-like inputs (0/1 or bool).")
        return M.mean(axis=0)
