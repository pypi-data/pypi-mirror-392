from __future__ import annotations
from typing import Optional, Union
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator
from sklearn.feature_selection import f_classif, chi2
from .basefs import FSMethod

try:
    from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
except Exception:
    mutual_info_classif = None
    mutual_info_regression = None

try:
    from scipy.stats import ttest_ind, pearsonr, spearmanr
except Exception:
    ttest_ind = None
    pearsonr = None
    spearmanr = None


def _argsort_desc_to_rank(scores: np.ndarray) -> np.ndarray:
    """
    Convert scores (higher is better) to ranks in {1..p} (1 = best).
    """
    order = np.argsort(-scores)           
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, scores.size + 1) 
    return ranks


class RankingFilter(FSMethod, BaseEstimator):
    """
    Unified ranking filter with multiple scorers.

    Parameters
    ----------
    scorer : {"anova","ttest","mi","chi2","pearson","spearman","variance"}
        Underlying univariate scorer. Higher is better.
    target_type : {"classification","regression"}
        Used to choose MI variant and validate scenarios.
    """

    def __init__(self, scorer: str = "anova", target_type: str = "classification", name: Optional[str] = None):
        super().__init__(name=name or f"RankingFilter[{scorer}]", target_type=target_type)
        self.scorer = scorer

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> "RankingFilter":
        X, y = self._check_input(X, y)
        X_np = X.values if isinstance(X, pd.DataFrame) else np.asarray(X)
        y_np = y.values if isinstance(y, (pd.Series, pd.DataFrame)) else np.asarray(y)

        scorer = self.scorer.lower()

        if scorer == "anova":
            if self.target_type != "classification":
                raise ValueError("ANOVA-F is defined for classification targets.")
            F, _ = f_classif(X_np, y_np)
            scores = np.nan_to_num(F, nan=0.0, posinf=np.finfo(float).max/2, neginf=0.0)

        elif scorer == "ttest":
            if ttest_ind is None:
                raise ImportError("scipy.stats.ttest_ind is required for t-test scorer.")
            classes = np.unique(y_np)
            if classes.size != 2:
                raise ValueError("t-test scorer requires exactly two classes.")
            mask = (y_np == classes[0])
            scores = np.zeros(X_np.shape[1], dtype=float)
            for j in range(X_np.shape[1]):
                t, _ = ttest_ind(X_np[mask, j], X_np[~mask, j], equal_var=False, nan_policy="omit")
                if np.isnan(t):
                    t = 0.0
                scores[j] = abs(t)

        elif scorer == "mi":
            if mutual_info_classif is None:
                raise ImportError("scikit-learn mutual_info_* is required for MI scorer.")
            if self.target_type == "classification":
                mi = mutual_info_classif(X_np, y_np, discrete_features="auto")
            elif self.target_type == "regression":
                mi = mutual_info_regression(X_np, y_np, discrete_features="auto")
            else:
                raise ValueError("target_type must be 'classification' or 'regression' for MI.")
            scores = np.asarray(mi, dtype=float)

        elif scorer == "chi2":
            X_shift = X_np
            if np.any(X_np < 0):
                X_shift = X_np - X_np.min(axis=0, keepdims=True)
            chi2_scores, _ = chi2(X_shift, y_np)
            scores = np.nan_to_num(chi2_scores, nan=0.0, posinf=np.finfo(float).max/2, neginf=0.0)

        elif scorer == "pearson":
            if pearsonr is None:
                raise ImportError("scipy.stats.pearsonr is required for pearson scorer.")
            scores = np.zeros(X_np.shape[1], dtype=float)
            for j in range(X_np.shape[1]):
                r, _ = pearsonr(X_np[:, j], y_np)
                if np.isnan(r):
                    r = 0.0
                scores[j] = abs(r)

        elif scorer == "spearman":
            if spearmanr is None:
                raise ImportError("scipy.stats.spearmanr is required for spearman scorer.")
            scores = np.zeros(X_np.shape[1], dtype=float)
            for j in range(X_np.shape[1]):
                r, _ = spearmanr(X_np[:, j], y_np)
                if np.isnan(r):
                    r = 0.0
                scores[j] = abs(r)

        elif scorer == "variance":
            scores = np.nan_to_num(np.var(X_np, axis=0), nan=0.0)

        else:
            raise ValueError(f"Unknown scorer '{self.scorer}'.")

        self.feature_importances_ = scores
        self.ranking_ = _argsort_desc_to_rank(scores)
        self._post_fit()
        return self