from __future__ import annotations
import numpy as np
import warnings
from .base import BinaryAggregator, BaseAggregator

try:
    from scipy.stats import binomtest, beta
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False


def _ensure_binary_matrix(results: np.ndarray) -> np.ndarray:
    """
    Ensure a 2D binary (0/1) matrix. Raise with a helpful message otherwise.
    """
    A = np.asarray(results)
    if A.ndim != 2:
        raise ValueError("Expected a 2D array of shape (n_bootstraps, n_features).")
    uniq = np.unique(A)
    if not set(np.round(uniq).astype(int)).issubset({0, 1}):
        raise ValueError("Subset aggregators expect a binary matrix (values in {0,1}).")
    return (A > 0).astype(int)


def _benjamini_hochberg(pvals: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Benjamini–Hochberg FDR control.
    Returns:
        rejected: boolean mask of discoveries
        qvals: BH-adjusted p-values (a.k.a. FDR q-values)
    """
    p = np.asarray(pvals, dtype=float)
    if p.ndim != 1:
        raise ValueError("p-values must be a 1D array.")
    n = p.size
    order = np.argsort(p)
    ranked = p[order]
    q = np.empty_like(ranked)
    prev = 1.0
    for i in range(n, 0, -1):
        val = ranked[i-1] * n / i
        prev = min(prev, val)
        q[i-1] = prev
    qvals = np.empty_like(q)
    qvals[order] = q
    rejected = qvals <= alpha
    return rejected, qvals


class MajorityVoteAggregator(BinaryAggregator):
    def __init__(self, top_k: int | None = None, threshold: float = 0.5):
        super().__init__(top_k=top_k)
        self.threshold = float(threshold)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        M = _ensure_binary_matrix(results)
        return M.mean(axis=0) 

    def fit(self, results: np.ndarray):
        freq = self.aggregate(results)
        mask = (freq >= self.threshold).astype(int)
        if self.top_k is not None and mask.sum() > self.top_k:
            idx_sel = np.where(mask == 1)[0]
            idx_sorted = idx_sel[np.argsort(-freq[idx_sel])]
            idx_keep = idx_sorted[: self.top_k]
            mask = np.zeros_like(mask)
            mask[idx_keep] = 1
        self._agg_result = freq
        self.selected_features_ = mask
        order = np.argsort(-freq)
        self.final_ranking_ = order[: self.top_k] if self.top_k is not None else order[mask[order] == 1]
        return self


class TopKBinaryAggregator(BinaryAggregator):
    def __init__(self, top_k: int):
        super().__init__(top_k=top_k)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        M = _ensure_binary_matrix(results)
        return M.mean(axis=0)

    def fit(self, results: np.ndarray):
        if self.top_k is None or self.top_k <= 0:
            raise ValueError("TopKBinaryAggregator requires a positive top_k.")
        freq = self.aggregate(results)
        order = np.argsort(-freq)[: self.top_k]
        mask = np.zeros_like(freq, dtype=int)
        mask[order] = 1
        self._agg_result = freq
        self.selected_features_ = mask
        self.final_ranking_ = order
        return self


class ThresholdAggregator(BinaryAggregator):
    def __init__(self, threshold: float = 0.5, top_k: int | None = None):
        super().__init__(top_k=top_k)
        self.threshold = float(threshold)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        M = _ensure_binary_matrix(results)
        return M.mean(axis=0)

    def fit(self, results: np.ndarray):
        freq = self.aggregate(results)
        mask = (freq >= self.threshold).astype(int)
        if self.top_k is not None and mask.sum() > self.top_k:
            idx_sel = np.where(mask == 1)[0]
            idx_sorted = idx_sel[np.argsort(-freq[idx_sel])]
            idx_keep = idx_sorted[: self.top_k]
            mask = np.zeros_like(mask)
            mask[idx_keep] = 1
        self._agg_result = freq
        self.selected_features_ = mask
        order = np.argsort(-freq)
        self.final_ranking_ = order[: self.top_k] if self.top_k is not None else order[mask[order] == 1]
        return self



class QuantileThresholdAggregator(BinaryAggregator):
    def __init__(self, q: float = 0.75, top_k: int | None = None):
        super().__init__(top_k=top_k)
        if not (0.0 <= q <= 1.0):
            raise ValueError("q must be in [0, 1].")
        self.q = float(q)

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        M = _ensure_binary_matrix(results)
        return M.mean(axis=0)

    def fit(self, results: np.ndarray):
        freq = self.aggregate(results)
        thr = np.quantile(freq, self.q)
        mask = (freq >= thr).astype(int)
        if self.top_k is not None and mask.sum() > self.top_k:
            idx_sel = np.where(mask == 1)[0]
            idx_sorted = idx_sel[np.argsort(-freq[idx_sel])]
            idx_keep = idx_sorted[: self.top_k]
            mask = np.zeros_like(mask)
            mask[idx_keep] = 1
        self._agg_result = freq
        self.selected_features_ = mask
        order = np.argsort(-freq)
        self.final_ranking_ = order[: self.top_k] if self.top_k is not None else order[mask[order] == 1]
        return self


class WeightedMajorityVoteAggregator(BinaryAggregator):
    def __init__(self, weights: np.ndarray | None = None, threshold: float | None = None, top_k: int | None = None):
        super().__init__(top_k=top_k)
        self.weights = None if weights is None else np.asarray(weights, dtype=float)
        self.threshold = threshold

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        M = _ensure_binary_matrix(results)
        B, p = M.shape
        if self.weights is None:
            w = np.ones(B, dtype=float) / B
        else:
            if self.weights.shape != (B,):
                raise ValueError(f"weights must have shape ({B},), got {self.weights.shape}.")
            if np.any(self.weights < 0):
                raise ValueError("weights must be non-negative.")
            s = self.weights.sum()
            if s <= 0:
                raise ValueError("sum(weights) must be > 0.")
            w = self.weights / s
        return (M.T @ w).astype(float)

    def fit(self, results: np.ndarray):
        freq_w = self.aggregate(results)
        p = freq_w.size
        thr = self.threshold if self.threshold is not None else (0.5 if self.top_k is None else -np.inf)
        mask = (freq_w >= thr).astype(int) if thr != -np.inf else np.ones(p, dtype=int)
        if self.top_k is not None:
            order = np.argsort(-freq_w)[: self.top_k]
            mask = np.zeros_like(freq_w, dtype=int)
            mask[order] = 1
            final_rank = order
        else:
            order = np.argsort(-freq_w)
            final_rank = order[mask[order] == 1]
        self._agg_result = freq_w
        self.selected_features_ = mask
        self.final_ranking_ = final_rank
        return self


class FDRControlledFrequencyAggregator(BinaryAggregator):
    def __init__(self, p0: float = 0.5, alpha: float = 0.1, score_mode: str = "neglog10q", top_k: int | None = None):
        super().__init__(top_k=top_k)
        if not (0.0 < p0 < 1.0):
            raise ValueError("p0 must be in (0,1).")
        if not (0.0 < alpha < 1.0):
            raise ValueError("alpha must be in (0,1).")
        if score_mode not in {"freq", "neglog10q"}:
            raise ValueError("score_mode must be 'freq' or 'neglog10q'.")
        self.p0 = float(p0)
        self.alpha = float(alpha)
        self.score_mode = score_mode
        self.q_values_ = None

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        M = _ensure_binary_matrix(results)
        return M.mean(axis=0)

    def fit(self, results: np.ndarray):
        M = _ensure_binary_matrix(results)
        B, p = M.shape
        k = M.sum(axis=0) 
        freq = k / B

        pvals = np.empty(p, dtype=float)
        if _HAS_SCIPY:
            for j in range(p):
                pvals[j] = binomtest(int(k[j]), n=B, p=self.p0, alternative='two-sided').pvalue
        else:
            mu = B * self.p0
            sigma = np.sqrt(B * self.p0 * (1 - self.p0))
            if sigma == 0:
                pvals[:] = 1.0
            else:
                from math import erf, sqrt
                def _phi(z): return 0.5 * (1 + erf(z / sqrt(2)))
                for j in range(p):
                    kj = k[j]
                    z = (kj + 0.5 - mu) / sigma if kj > mu else (kj - 0.5 - mu) / sigma
                    tail = 1 - _phi(abs(z))
                    pvals[j] = 2 * tail

        rejected, qvals = _benjamini_hochberg(pvals, self.alpha)
        self.q_values_ = qvals

        if self.score_mode == "neglog10q":
            q_safe = np.clip(qvals, 1e-300, 1.0)
            scores = -np.log10(q_safe)
        else:
            scores = freq

        mask = rejected.astype(int)
        if self.top_k is not None and mask.sum() > self.top_k:
            idx_sel = np.where(mask == 1)[0]
            idx_sorted = idx_sel[np.argsort(-scores[idx_sel])]
            idx_keep = idx_sorted[: self.top_k]
            new_mask = np.zeros_like(mask)
            new_mask[idx_keep] = 1
            mask = new_mask

        self._agg_result = scores
        self.selected_features_ = mask
        order = np.argsort(-scores)
        self.final_ranking_ = order[: self.top_k] if self.top_k is not None else order[mask[order] == 1]
        return self


class ClopperPearsonCIThresholdAggregator(BinaryAggregator):
    def __init__(self, alpha_ci: float = 0.05, t: float = 0.5, top_k: int | None = None):
        super().__init__(top_k=top_k)
        if not (0.0 < alpha_ci < 1.0):
            raise ValueError("alpha_ci must be in (0,1).")
        if not (0.0 <= t <= 1.0):
            raise ValueError("t must be in [0,1].")
        self.alpha_ci = float(alpha_ci)
        self.t = float(t)
        self.ci_lower_ = None
        self.ci_upper_ = None

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        M = _ensure_binary_matrix(results)
        return M.mean(axis=0)

    def fit(self, results: np.ndarray):
        if not _HAS_SCIPY:
            raise ImportError(
                "ClopperPearsonCIThresholdAggregator requires SciPy. "
                "Please install scipy or use a different subset aggregator."
            )
        M = _ensure_binary_matrix(results)
        B, p = M.shape
        k = M.sum(axis=0).astype(int)

        lower = np.zeros(p, dtype=float)
        upper = np.ones(p, dtype=float)
        a = self.alpha_ci / 2.0
        for j in range(p):
            kj = k[j]
            lower[j] = beta.ppf(a, kj, B - kj + 1) if kj > 0 else 0.0
            upper[j] = beta.ppf(1 - a, kj + 1, B - kj) if kj < B else 1.0

        mask = (lower >= self.t).astype(int)
        if self.top_k is not None and mask.sum() > self.top_k:
            idx_sel = np.where(mask == 1)[0]
            idx_sorted = idx_sel[np.argsort(-lower[idx_sel])]
            idx_keep = idx_sorted[: self.top_k]
            new_mask = np.zeros_like(mask)
            new_mask[idx_keep] = 1
            mask = new_mask

        self.ci_lower_ = lower
        self.ci_upper_ = upper
        scores = self.aggregate(results)  

        self._agg_result = scores
        self.selected_features_ = mask
        order = np.argsort(-scores)
        self.final_ranking_ = order[: self.top_k] if self.top_k is not None else order[mask[order] == 1]
        return self
