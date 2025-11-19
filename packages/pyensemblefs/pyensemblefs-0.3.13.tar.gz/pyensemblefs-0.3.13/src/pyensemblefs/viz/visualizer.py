from . import ranking, stability, comparison


class Visualizer:
    """
    High-level façade for visualization functions.
    Provides a single entry point but delegates work to specialized modules.
    """

    # Ranking
    consensus_ranking = staticmethod(ranking.consensus_ranking)
    plot_topk_frequency = staticmethod(ranking.plot_topk_frequency)

    # Stability
    feature_frequency = staticmethod(stability.feature_frequency)
    stability_heatmap = staticmethod(stability.stability_heatmap)
    stability_over_bootstraps = staticmethod(stability.stability_over_bootstraps)

    # Comparison
    compare_aggregators_heatmap = staticmethod(comparison.compare_aggregators_heatmap)
    cumulative_agreement_plot = staticmethod(comparison.cumulative_agreement_plot)
    pairwise_cumulative_agreement = staticmethod(comparison.pairwise_cumulative_agreement)
    topk_upset_plot = staticmethod(comparison.topk_upset_plot)
