from __future__ import annotations
from importlib.metadata import version, PackageNotFoundError

from . import datasets
from .api import get_config, compute_scores, extract_features

__all__ = [
  "aggregators","ensemble","estimators","fsmethods","selectors",
  "stability","tools","utils","viz",
  "datasets","get_config","compute_scores","extract_features"
]

def _get_version() -> str:
    try: return version("pyensemblefs")
    except PackageNotFoundError: return "0.0.0"

__version__ = _get_version()
