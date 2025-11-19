from abc import ABC, abstractmethod
import numpy as np


class BaseStability(ABC):
    """
    Base class for stability metrics across bootstrap feature selections
    """

    @abstractmethod
    def compute(self, results: np.ndarray) -> float:
        """
        Compute stability metric.

        Parameters
        ----------
        results : np.ndarray
            Shape (n_bootstraps, n_features)
            Binary or continuous feature selection results.

        Returns
        -------
        stability : float
            Stability score (higher = more stable).
        """
        pass
