from __future__ import annotations
import numpy as np
from .base import RankAggregator, ScoreAggregator
import warnings


def _scores_to_ranks_per_bootstrap(results: np.ndarray) -> np.ndarray:
    """
    Convert a (B x p) score matrix to a (B x p) rank matrix per bootstrap, with 1 = best.
    Assumes higher scores are better.
    """
    return np.argsort(np.argsort(-results, axis=1), axis=1) + 1


class MeanRankAggregator(RankAggregator):
    """Aggregate by the mean rank across bootstraps (lower = better)."""

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        S = np.asarray(results)
        if S.ndim != 2:
            raise ValueError("results must be a 2D array (n_bootstraps, n_features).")
        ranks = np.argsort(np.argsort(-S, axis=1), axis=1) + 1
        return ranks.mean(axis=0)


class MedianRankAggregator(RankAggregator):
    """Aggregate by the median rank across bootstraps (robust; lower = better)."""

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        S = np.asarray(results)
        if S.ndim != 2:
            raise ValueError("results must be a 2D array (n_bootstraps, n_features).")
        ranks = np.argsort(np.argsort(-S, axis=1), axis=1) + 1
        return np.median(ranks, axis=0)


class ConsensusRankAggregator(RankAggregator):
    """
    Generic consensus rank by averaging ranks (same as MeanRank but kept
    for semantic clarity and potential future changes).
    """

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        S = np.asarray(results)
        if S.ndim != 2:
            raise ValueError("results must be a 2D array (n_bootstraps, n_features).")
        ranks = np.argsort(np.argsort(-S, axis=1), axis=1) + 1
        return ranks.mean(axis=0)


class BordaFromRanksAggregator(ScoreAggregator):
    """
    Borda aggregation from RANK INPUT.

    Behavior:
      - If input is integer ranks in {1, …, p}, use them as-is.
      - If input looks like raw scores (floats) or ranks outside [1, p],
        automatically convert to integer ranks (1=best) using
        `_scores_to_ranks_per_bootstrap`.

    Output:
      - Borda points (higher = better), hence this class derives from ScoreAggregator.
    """

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        R = np.asarray(results)
        if R.ndim != 2:
            raise ValueError("results must be a 2D array (n_bootstraps, n_features).")

        n_boot, n_feat = R.shape

        needs_conversion = (not np.issubdtype(R.dtype, np.integer)) or (np.min(R) < 1) or (np.max(R) > n_feat)
        if needs_conversion:
            warnings.warn(
                (
                    "BordaFromRanksAggregator received non-integer or out-of-range values; "
                    "interpreting input as SCORES and converting to integer ranks automatically."
                ),
                UserWarning
            )
            R = _scores_to_ranks_per_bootstrap(R).astype(int)

        points = n_feat - R  
        return points.sum(axis=0).astype(float)


class TrimmedMeanRankAggregator(RankAggregator):
    """
    Aggregate per-bootstrap ranks using an alpha-trimmed mean.
    Trims a fraction 'alpha' on both tails before averaging.

    Parameters
    ----------
    alpha : float in [0, 0.5)
        Proportion to trim on each tail (e.g., 0.1 trims 10% lowest and 10% highest).
    """
    def __init__(self, top_k=None, alpha: float = 0.1):
        super().__init__(top_k=top_k)
        if not (0.0 <= alpha < 0.5):
            raise ValueError("alpha must be in [0, 0.5)")
        self.alpha = alpha

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        ranks = _scores_to_ranks_per_bootstrap(results)
        B, _ = ranks.shape
        lo = int(np.floor(self.alpha * B))
        hi = B - lo
        trimmed = np.sort(ranks, axis=0)[lo:hi, :]
        return trimmed.mean(axis=0)  # lower is better


class WinsorizedMeanRankAggregator(RankAggregator):
    """
    Aggregate per-bootstrap ranks using a winsorized mean:
    extreme ranks are clipped to alpha-quantiles before averaging.

    Parameters
    ----------
    alpha : float in [0, 0.5)
        Proportion to winsorize on each tail.
    """
    def __init__(self, top_k=None, alpha: float = 0.1):
        super().__init__(top_k=top_k)
        if not (0.0 <= alpha < 0.5):
            raise ValueError("alpha must be in [0, 0.5)")
        self.alpha = alpha

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        ranks = _scores_to_ranks_per_bootstrap(results).astype(float)
        lo_q = np.quantile(ranks, self.alpha, axis=0, method="nearest")
        hi_q = np.quantile(ranks, 1 - self.alpha, axis=0, method="nearest")
        ranks = np.maximum(ranks, lo_q)
        ranks = np.minimum(ranks, hi_q)
        return ranks.mean(axis=0) 


class GeometricMeanRankAggregator(RankAggregator):
    """
    Aggregate per-bootstrap ranks via geometric mean:
    exp(mean(log(rank))) — emphasizes consistently high positions.
    """
    def aggregate(self, results: np.ndarray) -> np.ndarray:
        ranks = _scores_to_ranks_per_bootstrap(results).astype(float)
        geo = np.exp(np.mean(np.log(ranks), axis=0))
        return geo 


class RankProductAggregator(RankAggregator):
    """
    Aggregate via rank-product across bootstraps (in log domain for stability).
    Sensitive to features consistently near the top.

    Returns the sum of log-ranks; lower is better.
    """
    def aggregate(self, results: np.ndarray) -> np.ndarray:
        ranks = _scores_to_ranks_per_bootstrap(results).astype(float)
        log_rp = np.sum(np.log(ranks), axis=0)
        return log_rp
