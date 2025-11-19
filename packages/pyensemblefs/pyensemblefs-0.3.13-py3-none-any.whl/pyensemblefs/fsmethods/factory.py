from __future__ import annotations
from typing import Callable, Dict, Tuple, Any, DefaultDict, List
from collections import defaultdict
import inspect
from .rank import RankingFilter
from .score import FisherScore, MIScore, CorrelationScore
from .subset import SubsetFilter
from .subset import FCBFSubset, CFSSubset, MRMRSubset 
from pyensemblefs.selectors import AnovaSelector, MutualInfoSelector, FisherSelector, VarianceSelector, RandomForestSelector, L1LogisticSelector, ReliefSelector

try:
    from pyensemblefs.fsmethods.score import LaplacianScore, HSICScore  
    _HAS_EXTRA_SCORES = True
except Exception:
    _HAS_EXTRA_SCORES = False

try:
    from pyensemblefs.selectors import RandomForestSelector, L1LogisticSelector
    has_model_based = True
except Exception:
    has_model_based = False


_REGISTRY: Dict[Tuple[str, str], Callable[..., Any]] = {}

_SIMPLE_REGISTRY: Dict[str, Any] = {}


def register_fs(kind: str, name: str, ctor: Callable[..., Any]) -> None:
    key = (kind.lower(), name.lower())
    _REGISTRY[key] = ctor
    
    if kind.lower() == "base":
        _SIMPLE_REGISTRY[name.lower()] = ctor


def make_fs(kind: str, name: str, **kwargs) -> Any:
    key = (kind.lower(), name.lower())
    if key not in _REGISTRY:
        disponibles = [n for (k, n) in _REGISTRY.keys() if k == kind.lower()]
        raise KeyError(
            f"FS method not registered for kind='{kind}' name='{name}'. "
            f"Available for kind='{kind}': {sorted(set(disponibles))}"
        )
    return _REGISTRY[key](**kwargs)


def available_fs() -> Dict[str, List[str]]:
    out: DefaultDict[str, List[str]] = defaultdict(list)
    for (k, n) in _REGISTRY.keys():
        out[k].append(n)
    return {k: sorted(v) for k, v in out.items()}


def get_fs_method(name: str, **kwargs) -> Any:
    key = (name or "").strip().lower()
    if key not in _SIMPLE_REGISTRY:
        available = ", ".join(sorted(_SIMPLE_REGISTRY.keys()))
        raise KeyError(
            f"Unknown feature-selection method '{name}'. " 
            f"Available base methods: {available}"
        )
    return _SIMPLE_REGISTRY[key](**kwargs)


FS_METHODS = tuple(sorted(_SIMPLE_REGISTRY.keys()))


def _make_safe_ctor(
    Cls: type,
    rename_map: Dict[str, str] | None = None,
    transform: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None,
    ) -> Callable[..., Any]:
    sig = inspect.signature(Cls.__init__)
    params = sig.parameters
    has_var_kw = any(p.kind == p.VAR_KEYWORD for p in params.values())
    valid_keys = set(k for k in params.keys() if k != "self")

    def ctor(**kw):
        d = dict(kw)

        if rename_map:
            for old, new in rename_map.items():
                if old in d and new not in d:
                    d[new] = d.pop(old)

        if transform:
            d = transform(d)

        if not has_var_kw:
            d = {k: v for k, v in d.items() if k in valid_keys}

        return Cls(**d)

    return ctor

register_fs("rank", "anova", lambda **kw: RankingFilter(scorer="anova", **kw))
register_fs("rank", "ttest", lambda **kw: RankingFilter(scorer="ttest", **kw))
register_fs("rank", "mi", lambda **kw: RankingFilter(scorer="mi", **kw))
register_fs("rank", "chi2", lambda **kw: RankingFilter(scorer="chi2", **kw))
register_fs("rank", "pearson", lambda **kw: RankingFilter(scorer="pearson", **kw))
register_fs("rank", "spearman", lambda **kw: RankingFilter(scorer="spearman", **kw))
register_fs("rank", "variance", lambda **kw: RankingFilter(scorer="variance", **kw))

register_fs("score", "fisher", lambda **kw: FisherScore(**kw))
register_fs("score", "mi", lambda **kw: MIScore(**kw))
register_fs("score", "correlation", lambda **kw: CorrelationScore(**kw))

register_fs("subset", "variance", lambda **kw: SubsetFilter(rule="variance", **kw))

register_fs("base", "anova", lambda **kw: AnovaSelector(k=kw.get("k")))
register_fs("base", "mi", lambda **kw: MutualInfoSelector(k=kw.get("k")))
register_fs("base", "fisher", lambda **kw: FisherSelector(k=kw.get("k")))
register_fs("base", "variance", lambda **kw: VarianceSelector(k=kw.get("k"), threshold=kw.get("threshold", 0.0)))
register_fs("base", "relief", lambda **kw: ReliefSelector(k=kw.get("k"), **{k: v for k, v in kw.items() if k != "k"}))


if has_model_based:
    register_fs("base", "rf", lambda **kw: RandomForestSelector(k=kw.get("k")))
    register_fs("base", "l1lr", lambda **kw: L1LogisticSelector(k=kw.get("k")))


if _HAS_EXTRA_SCORES:
    register_fs("score", "laplacian", lambda **kw: LaplacianScore(**kw)) 
    register_fs("score", "hsic", lambda **kw: HSICScore(**kw))      

register_fs("subset", "fcbf", _make_safe_ctor(FCBFSubset))
register_fs("subset", "cfs",  _make_safe_ctor(CFSSubset))

def _mrmr_transform(d: Dict[str, Any]) -> Dict[str, Any]:
    if "redundancy" not in d:
        m = d.get("method", d.get("mode", None))
        if isinstance(m, str):
            m_low = m.strip().lower()
            if m_low in ("miq", "mid", "mi"):
                d["redundancy"] = "mi"
            elif m_low in ("corr", "correlation", "pearson"):
                d["redundancy"] = "corr"
    d.pop("method", None)
    d.pop("mode", None)
    return d

register_fs("subset", "mrmr", _make_safe_ctor(MRMRSubset, rename_map=None, transform=_mrmr_transform))

FS_METHODS = tuple(sorted(_SIMPLE_REGISTRY.keys()))
__all__ = ["register_fs", "make_fs", "available_fs", "get_fs_method", "FS_METHODS"]