from __future__ import annotations
from typing import Optional, List, Dict, Any
import copy
import numpy as np

from joblib import Parallel, delayed
from sklearn.base import clone as sk_clone
from sklearn.utils import resample

try:
    from tqdm import tqdm
except Exception:
    tqdm = None


def _safe_clone(obj):
    """Try sklearn.clone first; if it fails, fallback to deepcopy."""
    try:
        return sk_clone(obj)
    except Exception:
        return copy.deepcopy(obj)


class MetaBootstrapper:
    """
    Heterogeneous bootstrapper: cycles or samples from multiple FS methods.
    Produces per-bootstrap binary supports (0/1) aligned to the original feature order.

    Attributes after fit:
    ---------------------
    results_      : np.ndarray, shape (B, p), int {0,1}  -> binary selection mask per bootstrap
    score_mat_    : np.ndarray | None, shape (B_s, p)    -> stacked scores (only rows where selector produced scores)
    rank_mat_     : np.ndarray | None, shape (B_r, p)    -> stacked ranks  (only rows where selector produced ranks)
    methods_used_ : List[str], length B                  -> selector class name used at each bootstrap
    """

    def __init__(self,
                 fs_methods: List[Any],
                 n_bootstraps: int = 30,
                 n_jobs: int = 1,
                 random_state: Optional[int] = None,
                 strategy: str = "sequential",           # "sequential" | "random" | "random_weighted"
                 normalize_scores: bool = True,
                 method_weights: Optional[Dict[str, float]] = None,
                 verbose: bool = True):
        """
        Parameters
        ----------
        fs_methods : list
            List of (already constructed) feature selectors with .fit() and either:
                - get_support(indices=...), or
                - ranking_ (1=best) and attribute k, or
                - feature_importances_ and attribute k.
        n_bootstraps : int
            Number of bootstrap resamples (B).
        n_jobs : int
            Parallel jobs (joblib).
        random_state : int or None
            Global seed for reproducibility.
        strategy : str
            Selector assignment per bootstrap: "sequential", "random", "random_weighted".
        normalize_scores : bool
            Min-max normalize scores per bootstrap row before stacking.
        method_weights : dict or None
            Optional per-selector weight applied to the score vector (by class name).
        verbose : bool
            If True, show progress bar (requires tqdm).
        """
        if not fs_methods or len(fs_methods) == 0:
            raise ValueError("fs_methods must be a non-empty list of selectors.")

        self.fs_methods = list(fs_methods)
        self.n_bootstraps = int(n_bootstraps)
        self.n_jobs = int(n_jobs)
        self.random_state = random_state
        self.strategy = str(strategy)
        self.normalize_scores = bool(normalize_scores)
        self.method_weights = dict(method_weights) if method_weights else {}
        self.verbose = bool(verbose)

        self.results_: Optional[np.ndarray] = None
        self.score_mat_: Optional[np.ndarray] = None
        self.rank_mat_: Optional[np.ndarray] = None
        self.methods_used_: List[str] = []


    def _normalize(self, scores: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """Normalize scores to [0, 1] per bootstrap row, if requested."""
        if scores is None or not self.normalize_scores:
            return scores
        scores = np.asarray(scores, dtype=float).ravel()
        min_val, max_val = np.min(scores), np.max(scores)
        if max_val <= min_val:
            return np.ones_like(scores, dtype=float)
        return (scores - min_val) / (max_val - min_val)

    def _mask_from_selector(self, fs, p: int) -> np.ndarray:
        """
        Build a 0/1 mask from a fitted selector 'fs' over p features.
        Priority:
            1) fs.get_support()
            2) fs.ranking_ + fs.k
            3) fs.feature_importances_ + fs.k
        """
        if hasattr(fs, "get_support"):
            mask = fs.get_support(indices=False).astype(int)
            if mask.shape[0] != p:
                raise ValueError(f"get_support returned length {mask.shape[0]}, expected {p}.")
            return mask

        k = getattr(fs, "k", None)
        if k is None:
            raise ValueError("Selector provides neither get_support nor 'k' to derive a mask.")

        if getattr(fs, "ranking_", None) is not None:
            order = np.argsort(fs.ranking_) 
            idx = order[: int(k)]
        elif getattr(fs, "feature_importances_", None) is not None:
            order = np.argsort(-np.asarray(fs.feature_importances_))
            idx = order[: int(k)]
        else:
            raise ValueError("Selector lacks get_support, ranking_, and feature_importances_.")

        mask = np.zeros(p, dtype=int)
        mask[idx] = 1
        return mask

    def _choose_index(self, rng: np.random.RandomState, b_idx: int) -> int:
        """Pick selector index according to assignment strategy."""
        m = len(self.fs_methods)
        if self.strategy == "sequential":
            return b_idx % m
        elif self.strategy == "random":
            return int(rng.randint(0, m))
        elif self.strategy == "random_weighted":
            weights = []
            for base_fs in self.fs_methods:
                cls_name = type(base_fs).__name__
                w = float(self.method_weights.get(cls_name, 1.0))
                weights.append(w)
            probs = np.asarray(weights, dtype=float)
            probs = probs / probs.sum()
            return int(rng.choice(m, p=probs))
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def _run_single_bootstrap(self, X: np.ndarray, y: np.ndarray, b_idx: int, seed: int) -> Dict[str, Any]:
        rng = np.random.RandomState(seed)

        Xb, yb = resample(X, y, replace=True, stratify=y, random_state=seed)

        j = self._choose_index(rng, b_idx)
        fs = _safe_clone(self.fs_methods[j])
        #method_name = type(fs).__name__
        base_name = type(fs).__name__
        method_name = base_name
        if base_name == "SelectKBest":
            sf = getattr(fs, "score_func", None)
            if sf is not None:
                sf_name = getattr(sf, "__name__", type(sf).__name__)
                method_name = f"{base_name}_{sf_name}"


        fs.fit(Xb, yb)

        p = X.shape[1]
        mask = self._mask_from_selector(fs, p) 
        
        '''
        scores = getattr(fs, "feature_importances_", None)
        if scores is not None:
            scores = np.asarray(scores, dtype=float).ravel()
            scores = self._normalize(scores)
            if method_name in self.method_weights:
                scores = scores * float(self.method_weights[method_name])

            ranks = np.argsort(scores)[::-1] 
            rankvec = np.empty(p, dtype=int)
            rankvec[ranks] = np.arange(1, p + 1)
        else:
            scorevec = None
            rankvec = None
            scores = scorevec
        '''
        
        scores = getattr(fs, "feature_importances_", None)
        if scores is None:
            scores = getattr(fs, "scores_", None)

        if scores is not None:
            scores = np.asarray(scores, dtype=float).ravel()
            scores = self._normalize(scores)

            # ponderación por método (ver abajo cómo se nombra)
            if method_name in self.method_weights:
                scores = scores * float(self.method_weights[method_name])
            else:
                # compat: permitir pesos definidos por nombre de clase
                cls_name = type(fs).__name__
                if cls_name in self.method_weights:
                    scores = scores * float(self.method_weights[cls_name])

            ranks = np.argsort(scores)[::-1] 
            rankvec = np.empty(p, dtype=int)
            rankvec[ranks] = np.arange(1, p + 1)
        else:
            scores = None
            rankvec = None

        return {
            "method": method_name,
            "mask": mask,
            "scores": scores,
            "ranks": rankvec
        }


    def fit(self, X: np.ndarray, y: np.ndarray):
        """Run B bootstraps; build binary selection matrix and optional score/rank stacks."""
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        n, p = X.shape

        rng = np.random.RandomState(self.random_state)
        seeds = rng.randint(0, 1_000_000, size=self.n_bootstraps)

        iterator = range(self.n_bootstraps)
        if self.verbose and tqdm is not None:
            iterator = tqdm(iterator, desc="Meta-bootstrapping", ncols=80)

        rows: List[np.ndarray] = []
        score_rows: List[np.ndarray] = []
        rank_rows: List[np.ndarray] = []
        methods_used: List[str] = []

        def _one(bi: int):
            return self._run_single_bootstrap(X, y, bi, int(seeds[bi]))

        results = Parallel(n_jobs=self.n_jobs)(
            delayed(_one)(bi) for bi in iterator
        )

        for r in results:
            rows.append(np.asarray(r["mask"], dtype=int))
            methods_used.append(str(r["method"]))
            if r["scores"] is not None:
                score_rows.append(np.asarray(r["scores"], dtype=float))
            if r["ranks"] is not None:
                rank_rows.append(np.asarray(r["ranks"], dtype=int))

        self.results_ = np.vstack(rows).astype(int)                  # (B, p)
        self.score_mat_ = np.vstack(score_rows) if score_rows else None
        self.rank_mat_ = np.vstack(rank_rows) if rank_rows else None
        self.methods_used_ = methods_used

        return self