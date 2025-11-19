# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, List, Sequence

import numpy as np
from scipy import sparse as sp

from .helpers import measure_score_helper

INTERSECTION_MEAN_VARIANT = "density"


def _submatrix_by_labels(sim_mat: sp.spmatrix | np.ndarray,
                         sim_labels: Sequence[Any],
                         F1: Sequence[Any], F2: Sequence[Any]) -> np.ndarray:
    idx = {u: i for i, u in enumerate(sim_labels)}
    i_idx = [idx[a] for a in F1 if a in idx]
    j_idx = [idx[b] for b in F2 if b in idx]
    if len(i_idx) == 0 or len(j_idx) == 0:
        return np.zeros((len(i_idx), len(j_idx)), dtype=float)
    C = sim_mat.tocsr() if sp.issparse(sim_mat) else np.asarray(sim_mat)
    if sp.issparse(C):
        return C[i_idx][:, j_idx].toarray()
    return C[np.ix_(i_idx, j_idx)]

def _apply_threshold(W: np.ndarray, threshold: float) -> np.ndarray:
    if threshold is None:
        return W
    M = W.copy()
    M[M < threshold] = 0.0
    return M

def _safe_denom_product(n1: int, n2: int) -> float:
    d = float(n1) * float(n2)
    return d if d > 0.0 else float("nan")


def _intersection_count_pair(W: np.ndarray) -> float:
    n1, n2 = W.shape
    denom = _safe_denom_product(n1, n2)
    if not np.isfinite(denom):
        return float("nan")
    Wb = (W > 0.0).astype(float)
    count = float(Wb.sum())
    return count / denom


def _intersection_mean_pair_density(W: np.ndarray) -> float:
    return _intersection_count_pair(W)


def _intersection_mean_pair(W: np.ndarray) -> float:
    return _intersection_count_pair(W)


def _intersection_greedy_pair(W: np.ndarray) -> float:
    return _intersection_count_pair(W)


def _intersection_mbm_pair(W: np.ndarray) -> float:
    return _intersection_count_pair(W)


def _intersection_generic(*, features: List[Sequence[Any]], F_all: Sequence[Any], sim_mat, sim_labels,
                          threshold: float, pair_fun) -> np.ndarray:
    assert sim_labels is not None, "sim_labels must be provided"
    assert threshold is not None, "threshold must be provided"

    def score_fun(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        if len(F1) == 0 or len(F2) == 0:
            return float("nan")
        W = _submatrix_by_labels(sim_mat, sim_labels, F1, F2)
        W = _apply_threshold(W, threshold)
        raw = pair_fun(W)  
        if not np.isfinite(raw):
            return float("nan")
        return raw

    return measure_score_helper(features=features, measureFun=score_fun)

def _intersection_count(*, features: List[Sequence[Any]], F_all: Sequence[Any], sim_mat, sim_labels, threshold: float, **_):
    return _intersection_generic(features=features, F_all=F_all, sim_mat=sim_mat, sim_labels=sim_labels,
                                 threshold=threshold, pair_fun=_intersection_count_pair)

def _intersection_mean(*, features: List[Sequence[Any]], F_all: Sequence[Any], sim_mat, sim_labels, threshold: float, **_):
    return _intersection_generic(features=features, F_all=F_all, sim_mat=sim_mat, sim_labels=sim_labels,
                                 threshold=threshold, pair_fun=_intersection_mean_pair)

def _intersection_greedy(*, features: List[Sequence[Any]], F_all: Sequence[Any], sim_mat, sim_labels, threshold: float, **_):
    return _intersection_generic(features=features, F_all=F_all, sim_mat=sim_mat, sim_labels=sim_labels,
                                 threshold=threshold, pair_fun=_intersection_greedy_pair)

def _intersection_mbm(*, features: List[Sequence[Any]], F_all: Sequence[Any], sim_mat, sim_labels, threshold: float, **_):
    return _intersection_generic(features=features, F_all=F_all, sim_mat=sim_mat, sim_labels=sim_labels,
                                 threshold=threshold, pair_fun=_intersection_mbm_pair)

def _intersection_common(*, features: List[Sequence[Any]], **kwargs):
    def score_fun(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        return float(len(set(F1).intersection(F2)))
    return measure_score_helper(features=features, measureFun=score_fun)

def _max_value_constant(**kwargs) -> float:
    return 1.0

# Export dicts (stabm-like)
intersection_greedy = {"scoreFun": _intersection_greedy, "maxValueFun": _max_value_constant}
intersection_mbm    = {"scoreFun": _intersection_mbm,    "maxValueFun": _max_value_constant}
intersection_count  = {"scoreFun": _intersection_count,  "maxValueFun": _max_value_constant}
intersection_mean   = {"scoreFun": _intersection_mean,   "maxValueFun": _max_value_constant}
intersection_common = {"scoreFun": _intersection_common, "maxValueFun": _max_value_constant}
