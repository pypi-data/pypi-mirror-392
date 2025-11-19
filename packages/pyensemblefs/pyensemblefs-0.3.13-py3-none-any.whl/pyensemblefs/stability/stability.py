# -*- coding: utf-8 -*-
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
from scipy import sparse as sp

from .helpers import measure_score_helper, row_means_without_zeros, col_means_without_zeros
from .measures_adjusted_intersections import (
    intersection_greedy,
    intersection_mbm,
    intersection_count,
    intersection_mean,
    intersection_common,
)
from .measures_adjusted_other import yu, zucknick, sechidis
from .measures_unadjusted import (
    davis,
    dice,
    hamming,
    jaccard,
    kappa_coefficient,
    lustgarten,
    nogueira,
    novovicova,
    ochiai,
    phi_coefficient,
    somol,
    wald,
)
from .expectations import simulate_expectation, calculate_expectation, unadjusted_expectation
from .config import (
    MEASURE_DEFAULT_CORR,
    N_ESTIMATE_DEFAULT,
    ADJUSTED_THRESHOLD_DEFAULT,
    SIM_EXP_BASE,        
    RETURN_ZERO_ON_DEGENERACY,
)

MEASURES: Dict[str, Dict[str, Any]] = {
    "intersection.greedy": intersection_greedy,
    "intersection.mbm": intersection_mbm,
    "intersection.count": intersection_count,
    "intersection.mean": intersection_mean,
    "intersection.common": intersection_common,
    "yu": yu,
    "zucknick": zucknick,
    "sechidis": sechidis,
    "davis": davis,
    "dice": dice,
    "hamming": hamming,
    "jaccard": jaccard,
    "kappa.coefficient": kappa_coefficient,
    "lustgarten": lustgarten,
    "nogueira": nogueira,
    "novovicova": novovicova,
    "ochiai": ochiai,
    "phi.coefficient": phi_coefficient,
    "somol": somol,
    "wald": wald,
}

ADJUSTED_MEASURES = {
    "yu",
    "zucknick",
    "sechidis",
    "intersection.mbm",
    "intersection.greedy",
    "intersection.count",
    "intersection.mean",
}

NEED_P = {
    "davis",
    "hamming",
    "intersection.common",
    "lustgarten",
    "phi.coefficient",
    "somol",
    "kappa.coefficient",
    "nogueira",
    "wald",
}

def _is_matrix_symmetric_dense(M: np.ndarray) -> bool:
    return np.allclose(M, M.T, rtol=0, atol=1e-12)

def _ensure_sparse_thresholded(sim_mat: Union[np.ndarray, sp.spmatrix], threshold: float) -> sp.coo_matrix:
    if sp.issparse(sim_mat):
        M = sim_mat.tocoo(copy=True)
    else:
        arr = np.asarray(sim_mat, dtype=float)
        if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
            raise ValueError("sim.mat must be a square matrix")
        if not _is_matrix_symmetric_dense(arr):
            raise ValueError("sim.mat must be symmetric")
        rows, cols = np.nonzero(arr >= threshold)
        data = arr[rows, cols]
        M = sp.coo_matrix((data, (rows, cols)), shape=arr.shape)

    if threshold is not None:
        keep = M.data >= float(threshold)
        M = sp.coo_matrix((M.data[keep], (M.row[keep], M.col[keep])), shape=M.shape)

    lower = M.row >= M.col
    M_lower = sp.coo_matrix((M.data[lower], (M.row[lower], M.col[lower])), shape=M.shape)
    M_sym = M_lower + M_lower.T - sp.diags(M_lower.diagonal())
    return M_sym.tocoo()

def _validate_features(features: List[Sequence[Any]]) -> bool:
    if not isinstance(features, list) or len(features) < 2:
        raise ValueError("features must be a list with length >= 2")
    type_char = [all(isinstance(x, str) for x in f) for f in features]
    type_int = [all(isinstance(x, (int, np.integer)) for x in f) for f in features]
    if any(type_char) and not all(type_char):
        raise ValueError("All features must be numeric or all must be character")
    if any(type_int) and not all(type_int) and not all(type_char):
        raise ValueError("All feature identifiers must share the same type")
    return any(type_char)

def stability(
    *,
    features: List[Sequence[Any]],
    measure: str,
    correction_for_chance: Optional[str],
    N: Optional[int],
    impute_na: Optional[float],
    p: Optional[int],
    sim_mat: Optional[Union[np.ndarray, sp.spmatrix]],
    sim_labels: Optional[List[Any]] = None,
    threshold: Optional[float] = None,
    penalty: Optional[float] = None,
) -> Optional[float]:
    # --- measure support ---
    if measure not in MEASURES:
        raise ValueError(f"Unsupported measure: {measure}")
    is_adj = measure in ADJUSTED_MEASURES

    # --- allow 'auto' and normalize correction mode ---
    # If auto/None -> use per-measure default from config; otherwise honor given (except special cases below).
    if correction_for_chance is None or correction_for_chance == "auto":
        corr_mode = MEASURE_DEFAULT_CORR.get(measure, "none")
    else:
        corr_mode = correction_for_chance


    if measure == "intersection.common":
        corr_mode = "unadjusted"  

   
    if corr_mode not in {"estimate", "exact", "none", "unadjusted"}:
        raise ValueError("correction.for.chance must be one of {'estimate','exact','none','auto'}")

    CORRECTED_ALREADY = {
        "kappa.coefficient",
        "lustgarten",
        "nogueira",
        "phi.coefficient",
        "somol",
        "wald",
    }
    if measure in CORRECTED_ALREADY and corr_mode != "none":
        logging.info(f"'{measure}' is already corrected; forcing correction_for_chance='none'.")
        corr_mode = "none"

    if measure == "sechidis" and corr_mode != "none":
        logging.info("Metric 'sechidis' does not support chance correction; forcing 'none'.")
        corr_mode = "none"

    if corr_mode == "estimate":
        if N is None or not isinstance(N, int) or N < 1:
            N = N_ESTIMATE_DEFAULT

    any_char = _validate_features(features)

    F_all: List[Any]
    sparse_C: Optional[sp.coo_matrix] = None

    if is_adj:
        if sim_mat is None:
            raise ValueError("Adjusted measures require sim.mat")
        if threshold is None:
            threshold = ADJUSTED_THRESHOLD_DEFAULT

        C = _ensure_sparse_thresholded(sim_mat, float(threshold))
        sparse_C = C.tocoo()

        if any_char:
            if sim_labels is None or len(sim_labels) != C.shape[0]:
                raise ValueError("sim.mat must have labels matching features (character mode)")
            F_all = list(sim_labels)
        else:
            F_all = list(range(1, C.shape[0] + 1))

        F_set = set(F_all)
        for f in features:
            if len(set(f)) != len(f):
                raise ValueError("Each feature set must have unique elements")
            if not set(f).issubset(F_set):
                raise ValueError("Feature set contains elements not in F.all")
    else:
        for f in features:
            if len(set(f)) != len(f):
                raise ValueError("Each feature set must have unique elements")
        if corr_mode != "none" or (measure in NEED_P):
            if p is None or not isinstance(p, int) or p < 1:
                raise ValueError("Parameter p must be provided and >=1 for this configuration")
            union_len = len(set().union(*[set(x) for x in features]))
            if union_len > p:
                raise ValueError("Union of features exceeds p")

    adjusted_intersections = {"intersection.mbm", "intersection.greedy", "intersection.mean", "intersection.count"}
    if measure in adjusted_intersections and sparse_C is not None and sparse_C.shape[0] > 1:
        any_sim = False
        if sparse_C.nnz > 0:
            any_sim = np.any(sparse_C.row != sparse_C.col)
        if not any_sim:
            logging.info("No similar features found under threshold; falling back to 'intersection.common'.")
            measure = "intersection.common"
            corr_mode = "unadjusted"
            is_adj = False
            if p is None:
                p = sparse_C.shape[0]

    mobj = MEASURES[measure]

    if is_adj:
        args: Dict[str, Any] = {
            "features": features,
            "F_all": F_all,
            "sim_mat": sparse_C,
            "sim_labels": sim_labels,
            "threshold": float(threshold),
        }
    else:
        args = {
            "features": features,
            "p": p,
            "penalty": penalty,
        }

    scores = np.asarray(mobj["scoreFun"](**args), dtype=float)

    if corr_mode != "none" and corr_mode != "unadjusted":
        if corr_mode == "estimate":
            expectation_fun = simulate_expectation
        elif corr_mode == "exact":
            expectation_fun = calculate_expectation
        else:
            expectation_fun = unadjusted_expectation 

        exp_args = dict(args)
        exp_args.update({"N": N, "fun": mobj["scoreFun"]})
        if not is_adj:
            exp_args.update({"F_all": list(range(1, p + 1))})
        expecteds = np.asarray(expectation_fun(**exp_args), dtype=float)

        maxima = np.asarray(mobj["maxValueFun"](**args), dtype=float)
        with np.errstate(invalid="ignore", divide="ignore"):
            denom = (maxima - expecteds)
            if RETURN_ZERO_ON_DEGENERACY:
                same = (
                    np.isfinite(scores) & np.isfinite(expecteds) & np.isfinite(maxima) &
                    (np.abs(scores - expecteds) < 1e-12) &
                    (np.abs(denom) < 1e-12)
                )
                adjusted = np.empty_like(scores, dtype=float)
                adjusted[same] = 0.0
                mask = ~same
                adjusted[mask] = (scores[mask] - expecteds[mask]) / denom[mask]
                scores = adjusted
            else:
                scores = (scores - expecteds) / denom

    if impute_na is not None:
        mask = np.isnan(scores)
        if mask.any():
            scores[mask] = float(impute_na)

    if scores.size == 0:
        return float("nan")
    return float(np.nanmean(scores)) if np.any(~np.isnan(scores)) else float("nan")