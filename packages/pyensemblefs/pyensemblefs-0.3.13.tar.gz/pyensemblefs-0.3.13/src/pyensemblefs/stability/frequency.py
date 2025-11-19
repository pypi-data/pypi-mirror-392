import numpy as np
from pyensemblefs.stability.base import BaseStability


class SelectionFrequencyStability(BaseStability):
    def compute(self, results: np.ndarray) -> float:
        freq = results.mean(axis=0)  
        return freq.mean() 


class EntropyStability(BaseStability):
    def compute(self, results: np.ndarray) -> float:
        p = results.mean(axis=0)
        p = np.clip(p, 1e-10, 1-1e-10)  
        entropy = -(p*np.log2(p) + (1-p)*np.log2(1-p))
        return 1 - entropy.mean()
