import warnings
from .rank import RankingFilter

class VarianceRanking(RankingFilter):
    def __init__(self, **kwargs):
        warnings.warn(
            "VarianceRanking is deprecated. Use RankingFilter(scorer='variance') instead.",
            DeprecationWarning, stacklevel=2
        )
        super().__init__(scorer="variance", **kwargs)
