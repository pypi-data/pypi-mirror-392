# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools as it
import logging
from typing import Any, Callable, List, Sequence

import numpy as np

from .helpers import measure_score_helper


def simulate_expectation(*, features: List[Sequence[Any]], F_all: Sequence[Any],
                         N: int, fun: Callable, rng: np.random.Generator | None = None, **kwargs):
    rng = np.random.default_rng() if rng is None else rng
    def exp_fun(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        ns = [len(F1), len(F2)]
        samples = [
            [rng.choice(F_all, size=ni, replace=False).tolist() for ni in ns]
            for _ in range(N)
        ]
        scores = [fun(features=s, F_all=F_all, **kwargs) for s in samples]
        vals = np.array([float(v[0]) if isinstance(v, (list, np.ndarray)) else float(v) for v in scores], dtype=float)
        return float(np.mean(vals))
    return measure_score_helper(features=features, measureFun=lambda a, b: exp_fun(a, b))

def calculate_expectation(*, features: List[Sequence[Any]], F_all: Sequence[Any], fun: Callable, **kwargs):
    p = len(F_all)

    def n_combs_pair(F1, F2):
        from math import comb
        return comb(p, len(F1)) * comb(p, len(F2))

    pairs_counts = measure_score_helper(features=features, measureFun=n_combs_pair)
    n_combs_total = int(np.sum(pairs_counts))
    if n_combs_total > 1_000_000:
        logging.warning("%d combinations needed for exact correction for chance. Computation may not be feasible!", n_combs_total)

    def exp_fun(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        ns = [len(F1), len(F2)]
        combs_single: List[List[List[Any]]] = []
        for ni in ns:
            if ni > 0:
                combs = list(it.combinations(F_all, ni))
                combs_single.append([list(c) for c in combs])
            else:
                combs_single.append([[]])
        samples = [list(x) for x in it.product(*combs_single)]
        scores = [fun(features=s, F_all=F_all, **kwargs) for s in samples]
        vals = np.array([float(v[0]) if isinstance(v, (list, np.ndarray)) else float(v) for v in scores], dtype=float)
        return float(np.mean(vals))

    return measure_score_helper(features=features, measureFun=lambda a, b: exp_fun(a, b))


def unadjusted_expectation(*, features: List[Sequence[Any]], F_all: Sequence[Any], **kwargs):
    p = len(F_all)

    def exp_fun(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        n1, n2 = len(F1), len(F2)
        return float(n1 * n2 / p)

    return measure_score_helper(features=features, measureFun=lambda a, b: exp_fun(a, b))