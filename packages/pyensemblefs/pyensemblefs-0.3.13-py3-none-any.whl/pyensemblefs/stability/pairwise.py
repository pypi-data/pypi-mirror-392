import numpy as np
from itertools import combinations
from pyensemblefs.stability.base import BaseStability


class KunchevaStability(BaseStability):

    def compute(self, results: np.ndarray) -> float:
        n_bootstraps, n_features = results.shape
        k = results.sum(axis=1).mean()
        if k == 0:
            return 0.0

        pairwise_scores = []
        for i, j in combinations(range(n_bootstraps), 2):
            overlap = np.sum(results[i] & results[j])
            pairwise_scores.append(overlap)

        avg_overlap = np.mean(pairwise_scores)
        
        return (avg_overlap - k**2 / n_features) / (k - k**2 / n_features)
