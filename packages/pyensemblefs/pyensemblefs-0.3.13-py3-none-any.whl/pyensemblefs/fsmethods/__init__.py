"""
Public API for fsmethods.
"""

from .basefs import FSMethod
from .rank import RankingFilter
from .score import FisherScore, MIScore, CorrelationScore
from .subset import SubsetFilter
from .factory import make_fs, register_fs

__all__ = [
    "FSMethod",
    "RankingFilter",
    "FisherScore",
    "MIScore",
    "CorrelationScore",
    "SubsetFilter",
    "make_fs",
    "register_fs",
]
