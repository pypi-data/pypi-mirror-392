from __future__ import annotations
import math
from typing import Any, List, Sequence

import numpy as np

from .helpers import measure_score_helper


def _davis_score(*, features: List[Sequence[Any]], p: int, penalty: float, **kwargs):
    n = len(features)
    n_chosen = np.array([len(f) for f in features], dtype=int)
    if np.all(n_chosen == 0):
        return np.array([float("nan")])
    all_features = [x for f in features for x in f]
    if len(all_features) == 0:
        return np.array([float("nan")])
    _, counts = np.unique(all_features, return_counts=True)
    part1 = counts.sum() / (n * len(_))
    median_f = int(np.median(n_chosen))
    part2 = (penalty or 0.0) * median_f / p
    score = max(0.0, part1 - part2)
    return np.array([float(score)])


def _dice_score(*, features: List[Sequence[Any]], **kwargs):
    def s(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        n1, n2 = len(F1), len(F2)
        if n1 == 0 and n2 == 0:
            return float("nan")
        inter = len(set(F1).intersection(F2))
        return 2.0 * inter / (n1 + n2) if (n1 + n2) > 0 else float("nan")
    return measure_score_helper(features=features, measureFun=s)


def _jaccard_score(*, features: List[Sequence[Any]], **kwargs):
    def s(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        n1, n2 = len(F1), len(F2)
        if n1 == 0 and n2 == 0:
            return float("nan")
        inter = len(set(F1).intersection(F2))
        union = len(set(F1).union(F2))
        return inter / union if union > 0 else float("nan")
    return measure_score_helper(features=features, measureFun=s)


def _lustgarten_score(*, features: List[Sequence[Any]], p: int, **kwargs):
    def s(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        n1, n2 = len(F1), len(F2)
        if n1 == 0 or n2 == 0 or n1 == p or n2 == p:
            return float("nan")
        inter = len(set(F1).intersection(F2))
        part1 = inter - n1 * n2 / p
        part2 = min(n1, n2) - max(0, n1 + n2 - p)
        return part1 / part2 if part2 != 0 else float("nan")
    return measure_score_helper(features=features, measureFun=s)


def _novovicova_score(*, features: List[Sequence[Any]], **kwargs):
    n = len(features)
    n_chosen = np.array([len(f) for f in features], dtype=int)
    if np.all(n_chosen == 0):
        return np.array([float("nan")])
    all_features = [x for f in features for x in f]
    _, counts = np.unique(all_features, return_counts=True)
    q = counts.sum()
    score = float(np.sum(counts * np.log2(counts)) / (q * np.log2(n)))
    return np.array([score])


def _ochiai_score(*, features: List[Sequence[Any]], **kwargs):
    def s(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        n1, n2 = len(F1), len(F2)
        if n1 == 0 or n2 == 0:
            return float("nan")
        inter = len(set(F1).intersection(F2))
        return inter / math.sqrt(n1 * n2) if (n1 > 0 and n2 > 0) else float("nan")
    return measure_score_helper(features=features, measureFun=s)


def _somol_score(*, features: List[Sequence[Any]], p: int, **kwargs):
    n = len(features)
    n_chosen = np.array([len(f) for f in features], dtype=int)
    if np.all(n_chosen == 0) or np.all(n_chosen == p):
        return np.array([float("nan")])
    all_features = [x for f in features for x in f]
    _, counts = np.unique(all_features, return_counts=True)
    q = counts.sum()
    c_min = (q**2 - p * (q - (q % p)) - (q % p) ** 2) / (p * q * (n - 1))
    c_max = ((q % n) ** 2 + q * (n - 1) - (q % n) * n) / (q * (n - 1))
    som = (np.sum(counts * (counts - 1)) / (q * (n - 1)) - c_min) / (c_max - c_min) if (c_max - c_min) != 0 else float("nan")
    return np.array([float(som)])


def _phi_coefficient_score(*, features: List[Sequence[Any]], p: int, **kwargs):
    def s(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        n1, n2 = len(F1), len(F2)
        if n1 == 0 or n2 == 0 or n1 == p or n2 == p:
            return float("nan")
        inter = len(set(F1).intersection(F2))
        num = inter - (n1 * n2) / p
        den = math.sqrt(n1 * (1 - n1 / p) * n2 * (1 - n2 / p))
        return float(num / den) if den != 0 else float("nan")
    return measure_score_helper(features=features, measureFun=s)


def _kappa_coefficient_score(*, features: List[Sequence[Any]], p: int, **kwargs):
    def s(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        n1, n2 = len(F1), len(F2)
        if (n1 == 0 and n2 == 0) or (n1 == p and n2 == p):
            return float("nan")
        inter = len(set(F1).intersection(F2))
        expected = n1 * n2 / p
        maximum = (n1 + n2) / 2.0
        denom = (maximum - expected)
        return float((inter - expected) / denom) if denom != 0 else float("nan")
    return measure_score_helper(features=features, measureFun=s)


def _nogueira_score(*, features: List[Sequence[Any]], p: int, **kwargs):
    ns = np.array([len(f) for f in features], dtype=float)
    ns_mean = float(np.mean(ns))
    if ns_mean == 0 or ns_mean == p:
        return np.array([float("nan")])
    n = len(features)
    all_features = [x for f in features for x in f]
    _, counts = np.unique(all_features, return_counts=True)
    freq = counts / n
    vars_ = freq * (1 - freq) * n / (n - 1) if n > 1 else np.zeros_like(freq)
    num = float(np.sum(vars_))
    denom = ns_mean * (1 - ns_mean / p)
    return np.array([float(1 - num / denom)])


def _wald_score(*, features: List[Sequence[Any]], p: int, **kwargs):
    def s(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        n1, n2 = len(F1), len(F2)
        if n1 == 0 or n2 == 0:
            return float("nan")
        inter = len(set(F1).intersection(F2))
        part1 = inter - n1 * n2 / p
        part2 = min(n1, n2) - n1 * n2 / p
        return float(part1 / part2) if part2 != 0 else float("nan")
    return measure_score_helper(features=features, measureFun=s)


def _hamming_score(*, features: List[Sequence[Any]], p: int, **kwargs):
    def s(F1: Sequence[Any], F2: Sequence[Any]) -> float:
        inter1 = len(set(F1).intersection(F2))
        inter2 = p - len(set(F1).union(F2))
        return float((inter1 + inter2) / p) if p > 0 else float("nan")
    return measure_score_helper(features=features, measureFun=s)



def _davis_max(*, features: List[Sequence[Any]], p: int, penalty: float, **kwargs):
    n = len(features)
    return np.array([max(1 - (penalty or 0.0) / p, ( (n - 1) // 2 ) / n)], dtype=float)

def _one_max(**kwargs):
    return np.array([1.0], dtype=float)


davis = {"scoreFun": _davis_score, "maxValueFun": _davis_max}
dice = {"scoreFun": _dice_score, "maxValueFun": _one_max}
jaccard = {"scoreFun": _jaccard_score, "maxValueFun": _one_max}
lustgarten = {"scoreFun": _lustgarten_score, "maxValueFun": _one_max}
novovicova = {"scoreFun": _novovicova_score, "maxValueFun": _one_max}
ochiai = {"scoreFun": _ochiai_score, "maxValueFun": _one_max}
somol = {"scoreFun": _somol_score, "maxValueFun": _one_max}
phi_coefficient = {"scoreFun": _phi_coefficient_score, "maxValueFun": _one_max}
kappa_coefficient = {"scoreFun": _kappa_coefficient_score, "maxValueFun": _one_max}
nogueira = {"scoreFun": _nogueira_score, "maxValueFun": _one_max}
wald = {"scoreFun": _wald_score, "maxValueFun": _one_max}
hamming = {"scoreFun": _hamming_score, "maxValueFun": _one_max}
