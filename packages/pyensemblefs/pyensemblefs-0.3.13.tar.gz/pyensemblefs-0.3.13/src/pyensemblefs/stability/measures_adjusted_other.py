from __future__ import annotations
from typing import Any, List, Sequence, Optional, Tuple

import numpy as np
from itertools import combinations
from scipy import sparse as sp
import networkx as nx
from itertools import combinations

from .helpers import measure_score_helper


def _coo_from_dense(A: np.ndarray) -> sp.coo_matrix:
    return sp.coo_matrix(A) if not sp.issparse(A) else A.tocoo()

def _cosel_matrix(F1: Sequence[Any], F2: Sequence[Any], universe: Sequence[Any]) -> Tuple[np.ndarray, np.ndarray]:
    idx = {u: i for i, u in enumerate(universe)}
    p = len(universe)
    x = np.zeros(p, dtype=float)
    y = np.zeros(p, dtype=float)
    for a in F1:
        if a in idx:
            x[idx[a]] = 1.0
    for b in F2:
        if b in idx:
            y[idx[b]] = 1.0
    return x, y

def yu(*, features: List[Sequence[Any]], F_all: Sequence[Any], sim_mat: sp.coo_matrix, **kwargs):
    import numpy as np
    import networkx as nx
    from itertools import combinations

    k = len(features)
    if k < 2:
        return [np.nan]

    sims = []
    for f1, f2 in combinations(features, 2):
        n1, n2 = len(f1), len(f2)
        if n1 == 0 or n2 == 0:
            sims.append(np.nan)
            continue

        idx = {u: i for i, u in enumerate(F_all)}
        i_idx = [idx[a] for a in f1 if a in idx]
        j_idx = [idx[b] for b in f2 if b in idx]
        if len(i_idx) == 0 or len(j_idx) == 0:
            sims.append(np.nan)
            continue

        C = sim_mat.tocsr()
        W = C[i_idx][:, j_idx].toarray() 

        G = nx.Graph()
        for i in range(len(i_idx)):
            G.add_node(("a", i), bipartite=0)
        for j in range(len(j_idx)):
            G.add_node(("b", j), bipartite=1)

        for i in range(len(i_idx)):
            for j in range(len(j_idx)):
                w = float(W[i, j])
                if w > 0.0:
                    G.add_edge(("a", i), ("b", j), weight=w)

        M = nx.algorithms.matching.max_weight_matching(G, maxcardinality=False, weight="weight")
        match_sum = 0.0
        for u, v in M:
            i = u[1] if u[0] == "a" else v[1]
            j = v[1] if v[0] == "b" else u[1]
            match_sum += float(W[i, j])

        denom = float(min(n1, n2))
        s = (match_sum / denom) if denom > 0 else np.nan
        sims.append(1.0 - s if np.isfinite(s) else np.nan)

    sims = np.array(sims, dtype=float)
    return [float(np.nanmean(sims))]


def zucknick(*, features: List[Sequence[Any]], F_all: Sequence[Any], sim_mat: sp.coo_matrix, **kwargs):
    import numpy as np
    from itertools import combinations

    k = len(features)
    if k < 2:
        return [np.nan]

    sims = []
    for f1, f2 in combinations(features, 2):
        s1, s2 = set(f1), set(f2)
        inter = len(s1 & s2)
        denom = np.sqrt(len(s1) * len(s2))
        sims.append((inter / denom) if denom > 0 else 0.0)

    sims = np.clip(sims, 0.0, 1.0)
    return [float(np.mean(sims))]


def sechidis(*, features: List[Sequence[Any]], F_all: Sequence[Any], sim_mat: sp.coo_matrix, **kwargs):
    import numpy as np
    from itertools import combinations

    k = len(features)
    if k < 2:
        return [np.nan]

    sims = []
    for f1, f2 in combinations(features, 2):
        s1, s2 = set(f1), set(f2)
        inter = len(s1 & s2)
        denom = min(len(s1), len(s2))
        sims.append((inter / denom) if denom > 0 else 0.0)

    sims = np.clip(sims, 0.0, 1.0)
    return [float(np.mean(sims))]


yu = {"scoreFun": yu, "maxValueFun": lambda **kwargs: measure_score_helper(features=kwargs["features"], measureFun=lambda a,b: (len(a)+len(b))/2.0)}
zucknick = {"scoreFun": zucknick, "maxValueFun": lambda **kwargs: measure_score_helper(features=kwargs["features"], measureFun=lambda a,b: 1.0)}
sechidis = {"scoreFun": sechidis, "maxValueFun": lambda **kwargs: np.array([float("nan")])}