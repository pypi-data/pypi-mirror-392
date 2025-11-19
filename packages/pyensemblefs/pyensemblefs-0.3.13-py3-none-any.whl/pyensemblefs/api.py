# -*- coding: utf-8 -*-
from __future__ import annotations
import logging
from typing import Optional, Tuple
import pandas as pd
import inspect

from pyensemblefs.configs import FSConfig, get_config as _get_config
from pyensemblefs.fsmethods.factory import get_fs_method, FS_METHODS
from pyensemblefs.ensemble.bootstrapper import Bootstrapper
from pyensemblefs.aggregators import rank as agg_rank
from pyensemblefs.aggregators import score as agg_score
from pyensemblefs.aggregators import subset as agg_subset
from pyensemblefs.aggregators import abcvote as agg_vote

LOG = logging.getLogger("pyensemblefs.api")

_LAST_SCORES: Optional[pd.DataFrame] = None

def get_config(name: str, **overrides) -> FSConfig:

    return _get_config(name, **overrides)

def _resolve_aggregator(name: str):
    key = (name or "").lower()
    if key == "voting":
        return agg_vote.ABCVoteAggregator()
    if key == "rank":
        return agg_rank.RankAggregator()
    if key == "score":
        return agg_score.ScoreAggregator()
    if key == "subset":
        return agg_subset.SubsetAggregator()
    raise KeyError(f"Unknown aggregator '{name}'")

def _resolve_selector(method: str, selector_kwargs: dict | None = None):
    key = (method or "").lower()
    if key == "relief":
        try:
            import skrebate
        except Exception:
            LOG.warning("Relief requested but 'scikit-rebate' is not installed; falling back to 'mi'.")
            key = "mi"
    return get_fs_method(key, **(selector_kwargs or {}))


def _make_bootstrapper(selector, n_bootstrap: int):
    """
    Build a Bootstrapper regardless of its __init__ signature.
    Tries common names for selector and n_bootstrap; falls back to attribute injection.
    """
    sig = inspect.signature(Bootstrapper.__init__)
    params = list(sig.parameters.keys())  # incl. 'self'

    # posibles nombres del selector en el ctor
    sel_keys = ["base_selector", "selector", "fs_method", "fsmethod"]
    # posibles nombres de n_bootstrap en el ctor
    n_keys = ["n_bootstrap", "n_bootstraps", "n_iter", "n_iters", "n_iterations", "B", "n"]

    kwargs = {}
    for k in sel_keys:
        if k in params:
            kwargs[k] = selector
            break

    nkey_ctor = None
    for k in n_keys:
        if k in params:
            nkey_ctor = k
            kwargs[k] = n_bootstrap
            break

    # intentar construcción directa con kwargs encontrados
    try:
        if "self" in params:
            params.remove("self")
        # si el ctor no tiene params y kwargs está vacío, simplemente instancie
        if not kwargs and len(params) == 0:
            bs = Bootstrapper()
        else:
            bs = Bootstrapper(**kwargs)
    except TypeError:
        # fallback: ctor sin kwargs; cree instancia "vacía"
        try:
            bs = Bootstrapper()
        except TypeError as e:
            raise TypeError(f"Unsupported Bootstrapper constructor: {sig}. Original error: {e}")

    # inyección por atributo si el ctor no aceptó n_bootstrap
    if nkey_ctor is None:
        for k in ["n_bootstrap", "n_bootstraps", "n_iter", "n_iters", "n_iterations", "B", "n"]:
            if hasattr(bs, k):
                setattr(bs, k, n_bootstrap)
                break

    # inyección del selector si el ctor no lo aceptó
    if not any(hasattr(bs, k) for k in sel_keys):
        # si el objeto tiene alguno de esos atributos, asígnelo
        for k in sel_keys:
            if hasattr(bs, k):
                setattr(bs, k, selector)
                break

    return bs


def _call_with_xy(fn, X, y, n_bootstrap: int | None = None):
    sig = inspect.signature(fn)
    params = [p for p in sig.parameters.keys() if p != "self"]

    n_keys = ["n_bootstrap", "n_bootstraps", "n_iter", "n_iters", "n_iterations", "B", "n"]

    kwargs = {}
    if n_bootstrap is not None:
        for k in n_keys:
            if k in params:
                kwargs[k] = n_bootstrap
                break

    if "X" in params and "y" in params:
        return fn(X=X, y=y, **kwargs)

    if len(params) >= 2:
        try:
            return fn(X, y, **kwargs)
        except TypeError:
            pass

    if len(params) == 1:
        try:
            return fn((X, y), **kwargs)
        except TypeError:
            pass

    try:
        return fn(**kwargs)
    except TypeError as e:
        raise TypeError(f"Incompatible callable signature {sig}: {e}")

def _run_bootstrap(bs, X, y, n_bootstrap: int):
    candidates = [
        "run", "run_bootstrap",
        "fit_transform", "fit_predict", "fit",
        "execute", "apply", "compute", "process", "__call__"
    ]

    def _as_results(ret):
        if ret is not None and not isinstance(ret, type(bs)):
            return ret
        if hasattr(bs, "results_") and bs.results_ is not None:
            return bs.results_
        raise AttributeError(
            "Bootstrap execution finished but no results were found. "
            "Expected 'results_' attribute on the Bootstrapper instance."
        )

    for name in candidates:
        if hasattr(bs, name):
            fn = getattr(bs, name)
            ret = _call_with_xy(fn, X, y, n_bootstrap)
            return _as_results(ret)

    if callable(bs):
        ret = _call_with_xy(bs, X, y, n_bootstrap)
        return _as_results(ret)

    methods = [m for m in dir(bs) if not m.startswith("_") and callable(getattr(bs, m))]
    raise AttributeError(
        "Bootstrapper object has no compatible execution method. "
        f"Tried: {candidates}. Public callables found: {methods}"
    )
    

def compute_scores(cfg: FSConfig, df: pd.DataFrame, target: str = "target") -> pd.DataFrame:
    if target not in df.columns:
        raise ValueError(f"target column '{target}' not found in DataFrame")

    X = df.drop(columns=[target])
    y = df[target]

    selector = _resolve_selector(cfg.method, cfg.selector_kwargs)
    aggregator = _resolve_aggregator(cfg.agg)

    bs = _make_bootstrapper(selector, n_bootstrap=cfg.n_bootstrap)
    boot_results = _run_bootstrap(bs, X, y, cfg.n_bootstrap)  

    df_scores = aggregator.aggregate(boot_results, feature_names=X.columns.tolist())

    global _LAST_SCORES
    _LAST_SCORES = df_scores.copy()
    return df_scores

def extract_features(n_max_features: int,
                     df_scores: Optional[pd.DataFrame] = None,
                     *, by: str = "score") -> Tuple[list[str], Optional[pd.DataFrame]]:

    global _LAST_SCORES
    if df_scores is None:
        if _LAST_SCORES is None:
            raise RuntimeError("No scores available. Call compute_scores(...) first or pass df_scores.")
        df_scores = _LAST_SCORES

    if by not in df_scores.columns:
        if "rank" in df_scores.columns:
            ordered = df_scores.sort_values("rank", ascending=True)
        else:
            raise ValueError(f"Cannot find column '{by}' in scores: {list(df_scores.columns)}")
    else:
        ordered = df_scores.sort_values(by, ascending=False)

    top = ordered.head(n_max_features)
    return top["feature"].tolist(), top
