# -*- coding: utf-8 -*-
"""
Unified public API for aggregators in pyensemblefs.

This module re-exports the most common aggregators from the score-, rank-, subset-
and ABC-voting modules, so users can simply do:

    from pyensemblefs.aggregators import (
        # Base types
        ScoreAggregator, RankAggregator, BinaryAggregator,
        # Score-based
        MeanAggregator, SumAggregator, MedianAggregator, WeightedScoreAggregator,
        BordaFromScoresAggregator, SelectionFrequencyAggregator,
        # Rank-based
        MeanRankAggregator, MedianRankAggregator, ConsensusRankAggregator,
        BordaFromRanksAggregator, TrimmedMeanRankAggregator,
        WinsorizedMeanRankAggregator, GeometricMeanRankAggregator, RankProductAggregator,
        # Subset-based
        ThresholdAggregator, MajorityVoteAggregator, TopKBinaryAggregator,
        # ABC-voting (generic + factory + catalog)
        ABCVotingRule, make_abcvoter, SAFE_RULES,
    )
"""

# ABC-voting (generic rule + factory + catalog)
from .abcvote import (
    ABCVotingRule,
    make_abcvoter,
    SAFE_RULES,
)

# Base classes
from .base import BaseAggregator, ScoreAggregator, RankAggregator, BinaryAggregator

# Score-based aggregators
from .score import (
    MeanAggregator,
    SumAggregator,
    MedianAggregator,
    WeightedScoreAggregator,
    BordaFromScoresAggregator,
    SelectionFrequencyAggregator,
)

# Rank-based aggregators
from .rank import (
    MeanRankAggregator,
    MedianRankAggregator,
    ConsensusRankAggregator,
    BordaFromRanksAggregator,
    TrimmedMeanRankAggregator,
    WinsorizedMeanRankAggregator,
    GeometricMeanRankAggregator,
    RankProductAggregator,
)

# Subset-based aggregators
from .subset import (
    ThresholdAggregator,
    MajorityVoteAggregator,
    TopKBinaryAggregator,
)

__all__ = [
    # base
    "BaseAggregator",
    "ScoreAggregator",
    "RankAggregator",
    "BinaryAggregator",

    # score-based
    "MeanAggregator",
    "SumAggregator",
    "MedianAggregator",
    "WeightedScoreAggregator",
    "BordaFromScoresAggregator",
    "SelectionFrequencyAggregator",

    # rank-based
    "MeanRankAggregator",
    "MedianRankAggregator",
    "ConsensusRankAggregator",
    "BordaFromRanksAggregator",
    "TrimmedMeanRankAggregator",
    "WinsorizedMeanRankAggregator",
    "GeometricMeanRankAggregator",
    "RankProductAggregator",

    # subset-based
    "ThresholdAggregator",
    "MajorityVoteAggregator",
    "TopKBinaryAggregator",

    # ABC-voting (generic only)
    "ABCVotingRule",
    "make_abcvoter",
    "SAFE_RULES",
]

