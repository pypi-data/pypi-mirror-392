from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd

class EnsembleFeatureSelector(BaseEstimator, TransformerMixin):
    """
    Glue component: Bootstrapper (produces per-bootstrap matrices) + Aggregator
    (produces ordered indices or a score vector) → final feature subset.
    """

    def __init__(self, bootstrapper, aggregator, k=None):
        """
        Parameters
        ----------
        bootstrapper : object
            Must implement fit(X, y) and set 'results_' (matrix expected by the aggregator).
        aggregator : object
            After fit(results_), must expose at least one of:
              - rank_   : ordered indices best→worst
              - scores_ : 1D vector (n_features,), higher = better
        k : int or None
            Final number of features to select. If None, returns all, ordered.
        """
        self.bootstrapper = bootstrapper
        self.aggregator = aggregator
        self.k = k
        self.selected_indices_ = None

    def _to_numpy(self, X):
        """Convert DataFrame to ndarray while preserving column/index metadata."""
        if pd is not None and isinstance(X, pd.DataFrame):
            return X.values, True, X.columns.to_numpy(), X.index
        return np.asarray(X), False, None, None

    def fit(self, X, y=None):
        """Fit bootstrapper and aggregator, then compute final ordered indices."""
        Xv, is_df, cols, idx = self._to_numpy(X)
        self.bootstrapper.fit(Xv, y)
        self.aggregator.fit(self.bootstrapper.results_)

        if hasattr(self.aggregator, "rank_") and self.aggregator.rank_ is not None:
            order = np.asarray(self.aggregator.rank_, dtype=int)
        elif hasattr(self.aggregator, "scores_") and self.aggregator.scores_ is not None:
            scores = np.asarray(self.aggregator.scores_).ravel()
            order = np.argsort(-scores, kind="mergesort")
        else:
            raise AttributeError(
                "Aggregator must expose 'rank_' (ordered indices) or 'scores_' (vector)."
            )

        self.selected_indices_ = order[: self.k] if self.k is not None else order
        return self

    def transform(self, X):
        """Select the columns given by selected_indices_."""
        if self.selected_indices_ is None:
            raise ValueError("Call fit() before transform().")
        Xv, is_df, cols, idx = self._to_numpy(X)
        Xt = Xv[:, self.selected_indices_]
        if is_df:
            import pandas as pd  
            return pd.DataFrame(Xt, columns=cols[self.selected_indices_], index=idx)
        return Xt