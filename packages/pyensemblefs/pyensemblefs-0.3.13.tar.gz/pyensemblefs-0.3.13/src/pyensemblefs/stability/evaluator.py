from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Sequence, Optional, Union, Any
import inspect
import numpy as np


try:
    from scipy import sparse as sp
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

from . import measures_unadjusted as mu
from . import measures_adjusted_other as mao



@dataclass
class StabilityResult:
    values: Dict[str, float]
    summary: float



class StabilityEvaluator:

    _REGISTRY: Dict[str, Any] = {
        # Uncorrected
        "jaccard":   mu.jaccard,
        "dice":      mu.dice,
        "ochiai":    mu.ochiai,
        "hamming":   mu.hamming,
        "novovicova": mu.novovicova,
        "davis":     mu.davis,
        # Corrected
        "lustgarten": mu.lustgarten,
        "phi":        mu.phi_coefficient,
        "kappa":      mu.kappa_coefficient,
        "nogueira":   mu.nogueira,
        # Adjusted (Other)
        "yu":        mao.yu,
        "zucknick":  mao.zucknick,
    }

    _ALL12: List[str] = [
        "jaccard", "dice", "ochiai", "hamming", "novovicova", "davis",
        "lustgarten", "phi", "kappa", "nogueira", "yu", "zucknick",
    ]

    def __init__(
        self,
        metrics: Union[str, Sequence[str]] = "all12",
        mode: str = "subset",
        sim_matrix: Optional[Union[np.ndarray, "sp.spmatrix"]] = None,
        penalty: float = 1.0,
    ):
        if isinstance(metrics, str):
            if metrics.lower() == "all12":
                metrics = list(self._ALL12)
            else:
                metrics = [metrics]
        self.metrics: List[str] = [m.lower() for m in metrics]
        self.mode = mode
        self.sim_matrix = sim_matrix
        self.penalty = float(penalty)

        self._resolved: Dict[str, Any] = {}
        for m in self.metrics:
            if m not in self._REGISTRY:
                raise ValueError(f"Metric '{m}' is not registered. Available: {list(self._REGISTRY.keys())}")
            self._resolved[m] = self._REGISTRY[m]


    @staticmethod
    def _results_to_feature_sets(results: np.ndarray) -> List[List[int]]:

        R = np.asarray(results)
        if R.ndim != 2:
            raise ValueError("results must be 2D (n_bootstraps, n_features).")
        if not np.all(np.isin(np.unique(np.rint(R)), [0, 1])):
            raise ValueError("For 'subset' mode, results must be binary or near-binary (0/1).")
        M = (np.rint(R) > 0).astype(int)
        feats = [list(np.where(M[b] == 1)[0]) for b in range(M.shape[0])]
        return feats

    @staticmethod
    def _filter_kwargs_for(func, full_kwargs: dict) -> dict:
        sig = inspect.signature(func)
        accepted = set(sig.parameters.keys())

        features = full_kwargs.get("features")
        p = full_kwargs.get("p")
        penalty = full_kwargs.get("penalty")
        sim_matrix = full_kwargs.get("sim_matrix")

        out = {}
        if "features" in accepted:
            out["features"] = features
        if "p" in accepted and p is not None:
            out["p"] = p
        if "penalty" in accepted and (penalty is not None):
            out["penalty"] = penalty

        if "F_all" in accepted and p is not None:
            out["F_all"] = list(range(int(p)))

        if ("sim_mat" in accepted) or ("sim_matrix" in accepted):
            if sim_matrix is None:
                if p is None:
                    raise ValueError("'p' is required to construct the similarity identity matrix.")
                if _HAS_SCIPY:
                    sim_prepared = sp.eye(int(p), format="coo")
                else:
                    sim_prepared = np.eye(int(p))
            else:
                if _HAS_SCIPY:
                    sim_prepared = sim_matrix.tocoo() if hasattr(sim_matrix, "tocoo") else sp.coo_matrix(sim_matrix)
                else:
                    sim_prepared = np.asarray(sim_matrix)
            if "sim_mat" in accepted:
                out["sim_mat"] = sim_prepared
            if "sim_matrix" in accepted:
                out["sim_matrix"] = sim_prepared

        return out

    @staticmethod
    def _call_metric_object(
        metric_obj: Any,
        *,
        features: List[Sequence[int]],
        p: int,
        penalty: float,
        sim_matrix: Optional[Union[np.ndarray, "sp.spmatrix"]],
    ) -> float:
        def _call(func):
            kwargs = StabilityEvaluator._filter_kwargs_for(
                func,
                dict(features=features, p=p, penalty=penalty, sim_matrix=sim_matrix),
            )
            out = func(**kwargs)
            arr = np.asarray(out)
            return float(arr.ravel()[0]) if arr.size > 0 else float("nan")

        if isinstance(metric_obj, dict):
            if "scoreFun" not in metric_obj:
                raise TypeError("The metric dict object must contain 'scoreFun'.")
            return _call(metric_obj["scoreFun"])
        elif callable(metric_obj):
            return _call(metric_obj)
        else:
            raise TypeError("Unsupported metric type. Use dict{'scoreFun', ...} or callable.")


    def compute(self, results: np.ndarray) -> StabilityResult:
        if self.mode.lower() != "subset":
            raise NotImplementedError("Currently only mode='subset' is supported.")

        R = np.asarray(results)
        if R.ndim != 2:
            raise ValueError("results must be 2D (n_bootstraps, n_features).")
        B, p = R.shape

        features = self._results_to_feature_sets(R)

        values: Dict[str, float] = {}
        for m, obj in self._resolved.items():
            v = self._call_metric_object(
                obj,
                features=features,
                p=p,
                penalty=self.penalty,
                sim_matrix=self.sim_matrix,
            )
            values[m] = v


        arr = np.array(list(values.values()), dtype=float)
        summary = float(np.nanmean(arr)) if arr.size > 0 else float("nan")
        return StabilityResult(values=values, summary=summary)
