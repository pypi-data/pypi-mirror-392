from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from typing import Union, List, Optional
from sklearn.base import BaseEstimator 


class FSMethod(ABC, BaseEstimator):
    """
    Abstract base class for all feature selection methods.
    Inherits from sklearn's BaseEstimator to support clone/get_params/set_params.
    """

    def __init__(self, name: str = None, target_type: str = None):
        """
        Initialize the feature selection method.

        Parameters
        ----------
        name : str, optional
            Name of the feature selection method.
        target_type : str, optional
            Type of target variable ('classification' or 'regression').
        """
        self.name = name or self.__class__.__name__
        self.target_type = target_type
        self.feature_importances_ = None
        self.selected_features_ = None
        self.ranking_ = None
        self._is_fitted = False

        self.categorical_features: Optional[List[str]] = None
        self.numerical_features: Optional[List[str]] = None

    @abstractmethod
    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray]
    ) -> "FSMethod":
        pass

    def transform(self,
              X: Union[pd.DataFrame, np.ndarray],
              threshold: Optional[float] = None,
              n_features: Optional[int] = None
              ) -> Union[pd.DataFrame, np.ndarray]:
        """
        Reduce X to the selected features.

        Selection priority:
        1) If n_features is provided and ranking_ exists -> take top-k by ranking_.
        2) Else if threshold is provided and feature_importances_ exists -> score >= threshold.
        3) Else -> use get_support() (selected_features_ or inferred "all True").

        Notes
        -----
        - This keeps backward-compatibility for subset methods while making score/rank
        methods usable without precomputing a binary mask.
        """
        if not self._is_fitted:
            raise ValueError("The feature selector has not been fitted yet. Call 'fit' first.")

        mask: Optional[np.ndarray] = None

        if n_features is not None and self.ranking_ is not None:
            k = int(n_features)
            p = len(self.ranking_)
            k = max(0, min(k, p))
            top_idx = np.argsort(self.ranking_)[:k]
            mask = np.zeros(p, dtype=bool)
            mask[top_idx] = True

        elif threshold is not None and self.feature_importances_ is not None:
            scores = np.asarray(self.feature_importances_)
            mask = scores >= float(threshold)
        
        else:
            mask = self.get_support(indices=False)

        if isinstance(X, pd.DataFrame):
            if self.feature_names_ is not None and len(mask) == len(self.feature_names_):
                return X.loc[:, mask]
            else:
                return X.iloc[:, np.flatnonzero(mask)]
        else:
            X_np = np.asarray(X)
            return X_np[:, np.flatnonzero(mask)]

        def fit_transform(
            self,
            X: Union[pd.DataFrame, np.array],
            y: Union[pd.Series, np.array],
            threshold: Optional[float] = None,
            n_features: Optional[int] = None
        ) -> Union[pd.DataFrame, np.ndarray]:
            self.fit(X, y)
            return self.transform(X, threshold=threshold, n_features=n_features)

    def get_support(self, indices: bool = False) -> Union[np.ndarray, List[str]]:
        """
        Get a mask, or integer index, of the features selected.

        If `selected_features_` is None (e.g., score/rank methods), infer a mask
        of all True using the length of `feature_importances_` or `ranking_`.
        """
        if not self._is_fitted:
            raise ValueError("The feature selector has not been fitted yet. Call 'fit' first.")

        support = self.selected_features_

        if support is None:
            if self.feature_importances_ is not None:
                p = len(self.feature_importances_)
                support = np.ones(p, dtype=bool)
            elif self.ranking_ is not None:
                p = len(self.ranking_)
                support = np.ones(p, dtype=bool)
            else:
                raise AttributeError(
                    f"{self.name} has neither selected_features_ nor artifacts to infer support."
                )

        support = np.asarray(support).astype(bool)

        if indices:
            return np.flatnonzero(support)
        return support


    def get_feature_importances(self) -> np.ndarray:
        if not self._is_fitted:
            raise ValueError("The feature selector has not been fitted yet. Call 'fit' first.")

        if self.feature_importances_ is None:
            raise AttributeError(f"{self.name} does not provide feature importances.")

        return self.feature_importances_

    def get_ranking(self) -> np.ndarray:
        if not self._is_fitted:
            raise ValueError("The feature selector has not been fitted yet. Call 'fit' first.")

        if self.ranking_ is None:
            raise AttributeError(f"{self.name} does not provide feature ranking.")

        return self.ranking_

    def _check_input(self, X, y):
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = X.columns.tolist()
        else:
            self.feature_names_ = None

        if len(X) != len(y):
            raise ValueError("X and y must have the same number of samples.")

        return X, y

    def _validate_params(self):
        pass

    def _post_fit(self):
        self._is_fitted = True
