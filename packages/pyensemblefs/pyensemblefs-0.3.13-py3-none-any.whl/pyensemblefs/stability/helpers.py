from __future__ import annotations
from typing import Any, Callable, List, Sequence, Optional

import numpy as np
from scipy import sparse as sp


def measure_score_helper(
    *, 
    features: List[Sequence[Any]], 
    measureFun: Callable[[Sequence[Any], Sequence[Any]], float]
) -> np.ndarray:

    n = len(features)
    scores: List[float] = []
    for i in range(n - 1):
        F1 = features[i]
        for j in range(i + 1, n):
            F2 = features[j]
            scores.append(measureFun(F1, F2))
    return np.asarray(scores, dtype=float)


def _means_without_zeros(data: np.ndarray, idx: np.ndarray, length: int) -> np.ndarray:
    res = np.zeros(length, dtype=float)
    if data.size == 0:
        return res
    order = np.argsort(idx)
    idx_sorted = idx[order]
    data_sorted = data[order]
    unique, starts = np.unique(idx_sorted, return_index=True)
    sums = np.add.reduceat(data_sorted, starts)
    counts = np.diff(np.append(starts, data_sorted.size))
    res[unique] = sums / counts
    return res


def row_means_without_zeros(M: sp.coo_matrix) -> np.ndarray:
    M = M.tocoo()
    return _means_without_zeros(M.data, M.row, M.shape[0])


def col_means_without_zeros(M: sp.coo_matrix) -> np.ndarray:
    M = M.tocoo()
    return _means_without_zeros(M.data, M.col, M.shape[1])



def to_coo_if_needed(mat: np.ndarray | sp.spmatrix, *, force_coo: bool = True) -> sp.coo_matrix | np.ndarray:
    if not force_coo:
        return mat
    if sp.issparse(mat):
        return mat.tocoo()
    return sp.coo_matrix(mat)


def normalize_similarity(sim: np.ndarray | sp.spmatrix) -> np.ndarray | sp.coo_matrix:
    if sp.issparse(sim):
        sim = sim.tocoo(copy=True)
        data = sim.data
        if data.size == 0:
            return sim
        mn = float(data.min())
        data = data - mn
        mx = float(data.max())
        if mx > 0:
            data = data / mx
        return sp.coo_matrix((data, (sim.row, sim.col)), shape=sim.shape)
    else:
        sim = np.asarray(sim, dtype=float)
        sim = sim - sim.min()
        mx = sim.max()
        if mx > 0:
            sim = sim / mx
        return sim


def build_similarity(
    X: np.ndarray,
    mode: str = "identity",
    *,
    sigma: float = 1.0,
    sparse_format: bool = True,
) -> np.ndarray | sp.coo_matrix:

    if X.ndim != 2:
        raise ValueError("X must be 2D: (n_samples, n_features)")
    _, p = X.shape

    mode_l = mode.lower()
    if mode_l == "identity":
        sim = np.eye(p, dtype=float)

    elif mode_l in {"corr", "abs-corr"}:
        sim = np.corrcoef(X, rowvar=False)
        sim = np.nan_to_num(sim, nan=0.0)
        if mode_l == "abs-corr":
            sim = np.abs(sim)

    elif mode_l == "rbf":
        Xf = np.asarray(X, dtype=float)
        gram = Xf.T @ Xf                       
        sq_norms = np.diag(gram)              
        D2 = sq_norms[:, None] + sq_norms[None, :] - 2.0 * gram
        D2 = np.maximum(D2, 0.0)               
        sim = np.exp(-(D2) / (2.0 * (sigma ** 2)))

    else:
        raise ValueError(f"Unknown mode '{mode}'. Choose from 'identity', 'corr', 'abs-corr', 'rbf'.")

    sim = (sim + sim.T) / 2.0
    sim = np.clip(sim, 0.0, 1.0)

    return to_coo_if_needed(sim, force_coo=sparse_format)


def build_exponential_similarity_from_labels(labels: Sequence[Any], base: float = 0.9) -> np.ndarray:
    p = len(labels)
    idx = np.arange(1, p + 1)
    return np.power(base, np.abs(idx.reshape(-1, 1) - idx.reshape(1, -1)))
