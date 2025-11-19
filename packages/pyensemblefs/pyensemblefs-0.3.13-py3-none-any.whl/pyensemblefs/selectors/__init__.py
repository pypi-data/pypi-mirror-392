# -*- coding: utf-8 -*-
from .base import BaseSelector
from .filters import AnovaSelector, MutualInfoSelector, FisherSelector, VarianceSelector
from .model_based import ReliefSelector

try:
    from .model_based import RandomForestSelector, L1LogisticSelector
    __all__ = [
        "BaseSelector",
        "AnovaSelector", "MutualInfoSelector", "FisherSelector", "VarianceSelector",
        "RandomForestSelector", "L1LogisticSelector",
    ]
except Exception:
    __all__ = [
        "BaseSelector",
        "AnovaSelector", "MutualInfoSelector", "FisherSelector", "VarianceSelector",
    ]

try:
    __all__.append("ReliefSelector")  # type: ignore[name-defined]
except Exception:
    __all__ = ["ReliefSelector"]