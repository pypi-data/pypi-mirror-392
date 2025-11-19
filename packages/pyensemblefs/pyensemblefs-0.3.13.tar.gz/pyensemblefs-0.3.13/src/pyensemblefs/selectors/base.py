from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
from sklearn.base import BaseEstimator


class BaseSelector(BaseEstimator, ABC):


    def __init__(self, k: Optional[int] = None, name: Optional[str] = None):
        self.k = k
        self.name = name or self.__class__.__name__
        self.selected_features_ = None
        self.ranking_ = None
        self.feature_importances_ = None

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseSelector":
        raise NotImplementedError


    def _ensure_outputs(self, p: int):
        if self.selected_features_ is None:
            self.selected_features_ = np.zeros(p, dtype=int)
        if self.ranking_ is None:
            self.ranking_ = np.arange(1, p + 1, dtype=int)
        if self.feature_importances_ is None:
            self.feature_importances_ = np.zeros(p, dtype=float)

    def get_support(self, indices: bool = False):
        if self.selected_features_ is None:
            raise RuntimeError("Selector is not fitted yet.")
        mask = np.asarray(self.selected_features_, dtype=bool)
        return np.flatnonzero(mask) if indices else mask

    def get_scores(self) -> np.ndarray:
        if self.feature_importances_ is None:
            raise RuntimeError("Selector is not fitted yet.")
        return np.asarray(self.feature_importances_, dtype=float)

    def get_ranking(self) -> np.ndarray:
        if self.ranking_ is None:
            raise RuntimeError("Selector is not fitted yet.")
        return np.asarray(self.ranking_, dtype=int)