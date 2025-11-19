import numpy as np
from joblib import Parallel, delayed
from sklearn.utils import resample
from sklearn.base import clone
from tqdm import tqdm

try:
    import pandas as pd
except Exception:
    pd = None


class Bootstrapper:
    """
    Run bootstrapped feature selection with parallelization.

    After fit(), exposes:
      - results_: np.ndarray of shape (B, p), either binary supports (0/1) or scores,
                  depending on the FS output availability (see _run_single).
      - selected_features_: will be populated if an external aggregator sets it later.
    """

    def __init__(self, fsmethod, n_bootstraps=50, n_jobs=-1, random_state=None, verbose=False):
        self.fsmethod = fsmethod
        self.n_bootstraps = n_bootstraps
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.verbose = verbose
        self.results_ = None
        self.selected_features_ = None

    def _run_single(self, X, y, seed):
        X_res, y_res = resample(X, y, random_state=seed)

        fs = clone(self.fsmethod)
        fs.fit(X_res, y_res)

        support_vec = None
        if hasattr(fs, "get_support"):
            try:
                support_mask = fs.get_support().astype(int)
                if support_mask.ndim != 1:
                    support_mask = support_mask.ravel()
                if support_mask.sum() > 0:
                    return support_mask 
                support_vec = support_mask  
            except Exception:
                support_vec = None

        if hasattr(fs, "feature_importances_") and fs.feature_importances_ is not None:
            scores = np.asarray(fs.feature_importances_).ravel()
            return scores

        if support_vec is not None:
            return support_vec

        raise ValueError(
            "Feature selection method must provide either non-empty support or feature_importances_."
        )

    def fit(self, X, y):
        if pd is not None and isinstance(X, pd.DataFrame):
            Xv = X.values
        else:
            Xv = np.asarray(X)

        rng = np.random.RandomState(self.random_state)
        seeds = rng.randint(0, 1_000_000, size=self.n_bootstraps)

        results = Parallel(n_jobs=self.n_jobs)(
            delayed(self._run_single)(Xv, y, int(seed))
            for seed in tqdm(seeds, disable=not self.verbose, desc="Bootstrapping")
        )

        self.results_ = np.vstack(results)
        return self

    def aggregate(self, aggregator):
        """
        Aggregate results using a provided Aggregator object.

        Contract:
          - aggregator.fit(self.results_) will be called.
          - If the aggregator exposes selected_features_, it will be copied here.
        """
        if self.results_ is None:
            raise RuntimeError("Call fit() first")

        aggregator.fit(self.results_)

        if hasattr(aggregator, "selected_features_"):
            self.selected_features_ = aggregator.selected_features_

        return aggregator
