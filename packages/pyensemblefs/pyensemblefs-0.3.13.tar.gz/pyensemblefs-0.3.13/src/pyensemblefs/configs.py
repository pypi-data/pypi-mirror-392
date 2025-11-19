# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Dict, Any

AggName = Literal["voting","rank","score","subset"]

@dataclass(frozen=True)
class FSConfig:
    method: str               
    n_bootstrap: int = 50
    agg: AggName = "voting"
    selector_kwargs: Dict[str, Any] = None

_REGISTRY = {
  "mi": FSConfig("mi", n_bootstrap=50, agg="score"),
  "fisher": FSConfig("fisher", n_bootstrap=50, agg="score"),
  "variance": FSConfig("variance", n_bootstrap=50, agg="score"),
  "anova": FSConfig("anova", n_bootstrap=50, agg="rank"),
  "rf": FSConfig("rf", n_bootstrap=50, agg="voting"),
  "l1lr": FSConfig("l1lr", n_bootstrap=50, agg="rank"),
  "relief": FSConfig("relief", n_bootstrap=100, agg="voting", selector_kwargs={"n_neighbors": 100, "k": None})
}

def get_config(name: str, **overrides) -> FSConfig:
    key = (name or "").strip().lower()
    if key not in _REGISTRY:
        raise KeyError(f"Unknown config '{name}'. Available: {sorted(_REGISTRY)}")
    base = _REGISTRY[key]
    d = dict(method=base.method, n_bootstrap=base.n_bootstrap, agg=base.agg,
             selector_kwargs=base.selector_kwargs or {})
    d.update(overrides)
    return FSConfig(**d)
