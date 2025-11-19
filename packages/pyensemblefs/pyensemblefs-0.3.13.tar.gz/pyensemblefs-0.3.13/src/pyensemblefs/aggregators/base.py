# -*- coding: utf-8 -*-
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class BaseAggregator(ABC):
    """
    Base class for aggregating feature selection results.

    Contract:
      - aggregate(results) -> 1D array (n_features,)
      - Input 'results' must be 2D: (n_bootstraps, n_features)
      - By default (ScoreAggregators), larger values are better.
      - Subclasses may override fit() to invert the criterion (e.g., RankAggregator).
    """

    def __init__(self, top_k: Optional[int] = None):
        self.top_k: Optional[int] = top_k
        self.final_ranking_: Optional[np.ndarray] = None     # indices ordered best→worst
        self.selected_features_: Optional[np.ndarray] = None # binary mask (1 selected)
        self._agg_result: Optional[np.ndarray] = None        # 1D aggregated vector (scores or ranks)
        self.n_features_: Optional[int] = None


    @staticmethod
    def _validate_results(results: np.ndarray) -> np.ndarray:
        """Ensure results is a numeric 2D array (n_bootstraps, n_features)."""
        if results is None:
            raise ValueError("`results` cannot be None.")
        arr = np.asarray(results)
        if arr.ndim != 2:
            raise ValueError(f"`results` must be 2D (n_bootstraps, n_features). Got shape={arr.shape}.")
        if arr.size == 0:
            raise ValueError("`results` is empty.")
        arr = np.nan_to_num(arr.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
        return arr

    @staticmethod
    def _clip_k(top_k: Optional[int], n_features: int) -> Optional[int]:
        if top_k is None:
            return None
        k = int(top_k)
        if k <= 0:
            raise ValueError(f"`top_k` must be positive. Got {top_k}.")
        return int(min(k, n_features))

    def set_top_k(self, top_k: Optional[int]) -> "BaseAggregator":
        """Set or update top_k after construction."""
        self.top_k = top_k
        return self


    @abstractmethod
    def aggregate(self, results: np.ndarray) -> np.ndarray:
        """
        Parameters
        ----------
        results : np.ndarray of shape (n_bootstraps, n_features)
            Per-bootstrap results to aggregate.

        Returns
        -------
        aggregated : np.ndarray of shape (n_features,)
            Aggregated vector (scores or ranks).
        """
        raise NotImplementedError


    def fit(self, results: np.ndarray):
        """Default fit: assumes higher aggregated values are better (score-like)."""
        res = self._validate_results(results)
        n_boot, n_feat = res.shape
        self.n_features_ = n_feat

        agg_result = np.asarray(self.aggregate(res)).ravel()
        if agg_result.shape[0] != n_feat:
            raise ValueError(f"aggregate() must return shape (n_features,), got {agg_result.shape}.")
        self._agg_result = agg_result

        k = self._clip_k(self.top_k, n_feat)
        sorted_indices = np.argsort(-agg_result, kind="mergesort")
        self.final_ranking_ = sorted_indices[:k] if k is not None else sorted_indices

        mask = np.zeros(n_feat, dtype=int)
        mask[self.final_ranking_] = 1
        self.selected_features_ = mask
        return self


    @property
    def scores_(self) -> Optional[np.ndarray]:
        """Return raw aggregated values (scores or ranks depending on subclass)."""
        return self._agg_result

    @property
    def rank_(self) -> Optional[np.ndarray]:
        """
        Return indices of features ordered best→worst.
        This is an ordered list of indices, NOT per-feature rank numbers.
        """
        return self.final_ranking_

    def get_support(self, indices: bool = False):
        """
        Scikit-learn-like support API.
        - If indices=False: returns boolean mask (n_features,)
        - If indices=True : returns selected indices (1D)
        """
        if self.selected_features_ is None:
            raise RuntimeError("Estimator not fitted yet; `selected_features_` is None.")
        mask_bool = np.asarray(self.selected_features_, dtype=bool)
        return np.flatnonzero(mask_bool) if indices else mask_bool


class ScoreAggregator(BaseAggregator):
    """Aggregators where higher score = better (use BaseAggregator.fit)."""
    pass


class RankAggregator(BaseAggregator):
    """
    Aggregators producing per-feature rank values, where LOWER = better.
    aggregate() must return per-feature rank values (e.g., mean rank).
    """
    def fit(self, results: np.ndarray):
        res = self._validate_results(results)
        n_boot, n_feat = res.shape
        self.n_features_ = n_feat

        rank_values = np.asarray(self.aggregate(res)).ravel()
        if rank_values.shape[0] != n_feat:
            raise ValueError(f"aggregate() must return shape (n_features,), got {rank_values.shape}.")
        self._agg_result = rank_values  

        k = self._clip_k(self.top_k, n_feat)
        sorted_indices = np.argsort(rank_values, kind="mergesort")
        self.final_ranking_ = sorted_indices[:k] if k is not None else sorted_indices

        mask = np.zeros(n_feat, dtype=int)
        mask[self.final_ranking_] = 1
        self.selected_features_ = mask
        return self


class BinaryAggregator(BaseAggregator):
    """
    Aggregators that produce a binary selection mask (0/1).
    aggregate() must return a 0/1 vector; fit() stores it and builds a stable order.
    """
    def fit(self, results: np.ndarray):
        res = self._validate_results(results)
        n_boot, n_feat = res.shape
        self.n_features_ = n_feat

        mask = np.asarray(self.aggregate(res)).astype(int).ravel()
        if mask.shape[0] != n_feat:
            raise ValueError(f"aggregate() must return shape (n_features,), got {mask.shape}.")
        mask = (mask > 0).astype(int)

        self._agg_result = mask
        self.selected_features_ = mask

        ones = np.where(mask == 1)[0]
        zeros = np.where(mask == 0)[0]
        order = np.concatenate([ones, zeros])
        k = self._clip_k(self.top_k, n_feat)
        self.final_ranking_ = order[:k] if k is not None else order
        return self