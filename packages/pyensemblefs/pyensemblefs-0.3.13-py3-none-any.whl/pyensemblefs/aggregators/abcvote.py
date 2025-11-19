from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Callable, Dict, List, Set, Optional

from .base import ScoreAggregator
from abcvoting.preferences import Profile
from abcvoting import abcrules as _abcr
from abcvoting.abcrules import Rule


def _committee_ids_from_abcvoting_object(obj) -> Set[int]:
    if isinstance(obj, (list, tuple)) and len(obj) > 0 and not isinstance(obj, set):
        obj = obj[0]

    try:
        return set(int(x) for x in obj)
    except Exception:
        pass

    try:
        return set(int(getattr(x, "id")) for x in obj)
    except Exception:
        pass

    if hasattr(obj, "aslist"):
        try:
            return set(int(x) for x in obj.aslist())
        except Exception:
            pass

    if isinstance(obj, set):
        try:
            return set(int(x) for x in list(obj))
        except Exception:
            pass

    raise TypeError(
        f"Cannot normalize abcvoting committee object of type {type(obj)} to a set of ints."
    )


def _pick_safe_algorithm(rule_id: str, prefer: Optional[List[str]] = None) -> Optional[str]:
    """Return an algorithm for rule_id that does not depend on Gurobi."""
    try:
        algos = tuple(a for a in Rule(rule_id).algorithms if "gurobi" not in a.lower())
    except Exception:
        return None
    if not algos:
        return None
    prefer = prefer or []
    for a in prefer:
        if a in algos:
            return a
    return algos[0]



class _ABCBase(ScoreAggregator):
    """Base class for ABC voting aggregators using `abcvoting`."""

    rule_name_: str = "ABC-Rule"

    def __init__(self, top_k: int):
        super().__init__(top_k=top_k)
        if top_k is None or int(top_k) <= 0:
            raise ValueError("top_k (committee size) must be a positive integer.")
        self._committee_: Set[int] | None = None

    def _build_profile(self, R: np.ndarray) -> Profile:
        if R.ndim != 2:
            raise ValueError("results must be a 2D array (n_bootstraps, n_features).")
        if not np.array_equal(R, R.astype(int)):
            raise ValueError(f"{self.rule_name_} expects binary 0/1 results.")
        n_boot, n_feat = R.shape
        approvals = [set(np.where(R[b] == 1)[0].tolist()) for b in range(n_boot)]
        profile = Profile(n_feat)
        profile.add_voters(approvals)
        return profile

    @staticmethod
    def _scores_av(R: np.ndarray) -> np.ndarray:
        return R.sum(axis=0).astype(float)

    @staticmethod
    def _scores_sav(R: np.ndarray) -> np.ndarray:
        row_sums = R.sum(axis=1)
        scores = np.zeros(R.shape[1], dtype=float)
        for b in range(R.shape[0]):
            m = int(row_sums[b])
            if m > 0:
                scores += (R[b] / float(m))
        return scores

    _scores_slav = _scores_sav  # same logic

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def fit(self, results: np.ndarray):
        agg_result = self.aggregate(results)
        sorted_indices = np.argsort(-agg_result)
        self.final_ranking_ = sorted_indices[: self.top_k]
        n_feat = results.shape[1]
        mask = np.zeros(n_feat, dtype=int)
        if self._committee_ is None:
            mask[self.final_ranking_] = 1
        else:
            for j in self._committee_:
                mask[int(j)] = 1
        self.selected_features_ = mask
        self._agg_result = agg_result
        return self



class ABCVotingRule(_ABCBase):
    """Generic aggregator for any `abcvoting` rule (without Gurobi)."""

    def __init__(
        self,
        top_k: int,
        compute_func: Callable,
        rule_id: Optional[str] = None,
        score_mode: str = "av",
        prefer_algorithms: Optional[List[str]] = None,
        **extra_kwargs,
    ):
        super().__init__(top_k=top_k)
        self.compute_func = compute_func
        self.rule_id = rule_id
        self.score_mode = score_mode.lower()
        self.prefer_algorithms = prefer_algorithms or []
        self.extra_kwargs = {"resolute": True, **extra_kwargs}
        self.rule_name_ = getattr(compute_func, "__name__", rule_id or "ABC-Rule")

    def aggregate(self, results: np.ndarray) -> np.ndarray:
        R = np.asarray(results)
        profile = self._build_profile(R)
        if "algorithm" not in self.extra_kwargs and self.rule_id is not None:
            safe_alg = _pick_safe_algorithm(self.rule_id, self.prefer_algorithms)
            if safe_alg is not None:
                self.extra_kwargs["algorithm"] = safe_alg
        committees = self.compute_func(profile, committeesize=int(self.top_k), **self.extra_kwargs)
        self._committee_ = _committee_ids_from_abcvoting_object(committees)
        if self.score_mode == "sav":
            return self._scores_sav(R)
        if self.score_mode == "slav":
            return self._scores_slav(R)
        return self._scores_av(R)





SAFE_RULES: Dict[str, Dict] = {
"av": {"rule_id": "av", "func": _abcr.compute_av, "score": "av", "prefer": ["standard"]},
"sav": {"rule_id": "sav", "func": _abcr.compute_sav, "score": "sav", "prefer": ["standard"]},
"slav": {"rule_id": "slav", "func": _abcr.compute_slav, "score": "slav", "prefer": ["standard"]},
"seqpav": {"rule_id": "seqpav", "func": _abcr.compute_seqpav, "score": "sav", "prefer": ["standard"]},
"seqslav": {"rule_id": "seqslav", "func": _abcr.compute_seqslav, "score": "slav", "prefer": ["standard"]},
"seqphragmen": {"rule_id": "seqphragmen", "func": _abcr.compute_seqphragmen, "score": "sav", "prefer": ["float-fractions", "standard-fractions", "gmpy2-fractions"]},
"seqcc": {"rule_id": "seqcc", "func": _abcr.compute_seqcc, "score": "sav", "prefer": ["standard"]},
"revseqpav": {"rule_id": "revseqpav", "func": _abcr.compute_revseqpav, "score": "sav", "prefer": ["standard"]},
"phragmen_enestroem":{"rule_id": "phragmen-enestroem","func": _abcr.compute_phragmen_enestroem,"score": "sav", "prefer": ["standard"]},
"equal_shares": {"rule_id": "equal-shares", "func": _abcr.compute_equal_shares, "score": "sav", "prefer": ["float-fractions", "standard-fractions", "gmpy2-fractions"]},
"rule_x": {"rule_id": "rule-x", "func": _abcr.compute_rule_x, "score": "sav", "prefer": ["float-fractions", "standard-fractions", "gmpy2-fractions"]},
"consensus_rule": {"rule_id": "consensus-rule", "func": _abcr.compute_consensus_rule, "score": "av", "prefer": ["float-fractions", "standard-fractions", "gmpy2-fractions"]},
"eph": {"rule_id": "eph", "func": _abcr.compute_eph, "score": "sav", "prefer": ["float-fractions", "standard-fractions", "gmpy2-fractions"]},
"rsd": {"rule_id": "rsd", "func": _abcr.compute_rsd, "score": "av", "prefer": ["standard"]},
"pav": {"rule_id": "pav", "func": _abcr.compute_pav, "score": "sav", "prefer": ["branch-and-bound", "brute-force", "mip-cbc"]},
"cc": {"rule_id": "cc", "func": _abcr.compute_cc, "score": "sav", "prefer": ["branch-and-bound", "brute-force", "mip-cbc", "ortools-cp"]},
"monroe": {"rule_id": "monroe", "func": _abcr.compute_monroe, "score": "sav", "prefer": ["brute-force", "mip-cbc", "ortools-cp"]},
"greedy_monroe": {"rule_id": "greedy-monroe", "func": _abcr.compute_greedy_monroe, "score": "sav", "prefer": ["standard"]},
"lexcc": {"rule_id": "lexcc", "func": _abcr.compute_lexcc, "score": "sav", "prefer": ["brute-force"]},
"lexminimaxav": {"rule_id": "lexminimaxav", "func": _abcr.compute_lexminimaxav, "score": "av", "prefer": ["brute-force"]},
"maximin_support": {"rule_id": "maximin-support", "func": _abcr.compute_maximin_support, "score": "sav", "prefer": ["mip-cbc"]},
"minimaxphragmen": {"rule_id": "minimaxphragmen", "func": _abcr.compute_minimaxphragmen, "score": "sav", "prefer": ["mip-cbc"]},
}


def make_abcvoter(rule_id: str, top_k: int, **kwargs) -> ABCVotingRule:
    """
    Factory for creating an ABCVotingRule from the SAFE_RULES catalog.

    Example
    -------
    >>> agg = make_abcvoter("seqpav", top_k=10)
    >>> agg.fit(R_binary)
    """
    rid = rule_id.lower()
    if rid not in SAFE_RULES:
        raise ValueError(
            f"Rule '{rule_id}' not available. "
            f"Available: {list(SAFE_RULES.keys())}"
        )
    spec = SAFE_RULES[rid]
    prefer_algorithms = list(spec.get("prefer", []))
    if "prefer_algorithms" in kwargs:
        prefer_algorithms = list(kwargs.pop("prefer_algorithms")) + prefer_algorithms
    return ABCVotingRule(
        top_k=top_k,
        compute_func=spec["func"],
        rule_id=spec.get("rule_id"),
        score_mode=spec["score"],
        prefer_algorithms=prefer_algorithms,
        **kwargs,
    )


class ABCVoteAggregator:
    """
    Adapter that wraps ABCVotingRule to the simple aggregator interface:
    - aggregate(boot_results, feature_names) -> DataFrame ['feature','score'] sorted desc.
    - boot_results can be:
        * iterable of subsets (names or indices), or
        * iterable of 1D binary masks (len = n_features).
    """
    def __init__(self, rule: str = "seqpav", top_k: int | None = None,
                 prefer_algorithms: Optional[List[str]] = None, **kwargs):
        self.rule = (rule or "seqpav").lower()
        self.top_k = top_k  # if None, we infer a reasonable k from the data
        self.prefer_algorithms = list(prefer_algorithms or [])
        self.kwargs = dict(kwargs)

    def _to_binary_matrix(self, boot_results, feature_names: List[str]) -> np.ndarray:
        n = len(feature_names)
        results = list(boot_results)
        R = np.zeros((len(results), n), dtype=int)
        for b, res in enumerate(results):
            if isinstance(res, (list, tuple, set)):
                if len(res) == 0:
                    continue
                first = next(iter(res))
                if isinstance(first, str):
                    idxs = [feature_names.index(f) for f in res if f in feature_names]
                else:
                    idxs = list(res)
                R[b, idxs] = 1
            else:
                arr = np.asarray(res)
                if arr.ndim != 1 or arr.shape[0] != n:
                    raise ValueError("Each bootstrap result must be a 1D mask with length = n_features.")
                R[b, :] = (arr > 0).astype(int)
        return R

    def aggregate(self, boot_results, feature_names: List[str]) -> pd.DataFrame:
        feature_names = list(feature_names)
        R = self._to_binary_matrix(boot_results, feature_names)

        # Infer a reasonable committee size if not provided (median approvals per bootstrap)
        if self.top_k is None:
            per_boot = R.sum(axis=1)
            k = int(np.median(per_boot)) if per_boot.size > 0 else 1
            k = max(1, min(k, len(feature_names)))
        else:
            k = int(self.top_k)

        voter = make_abcvoter(self.rule, top_k=k, prefer_algorithms=self.prefer_algorithms, **self.kwargs)
        scores = voter.aggregate(R)  # np.ndarray length = n_features

        df = pd.DataFrame({"feature": feature_names, "score": scores})
        return df.sort_values("score", ascending=False, ignore_index=True)

# ensure symbol is exported
try:
    __all__.append("ABCVoteAggregator")  # type: ignore[name-defined]
except Exception:
    __all__ = ["ABCVoteAggregator"]
