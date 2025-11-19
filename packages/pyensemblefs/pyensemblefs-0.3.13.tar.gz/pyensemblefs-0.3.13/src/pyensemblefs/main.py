from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif

# Use absolute imports consistent with the refactor
from pyensemblefs.ensemble.bootstrapper import Bootstrapper
from pyensemblefs.aggregators.score import MeanAggregator, SumAggregator, BordaFromScoresAggregator
from pyensemblefs.aggregators.rank import MeanRankAggregator
from pyensemblefs.viz.visualizer import Visualizer


# Load data as DataFrame to keep feature names
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
col_names = X.columns.values.tolist()
X = X.values  # convert to numpy for downstream components

print(X.shape)
print(y.shape)

# Choose base univariate FS (scores per feature)
# fs = SelectKBest(score_func=f_classif, k=10)
fs = SelectKBest(score_func=mutual_info_classif, k=20)

# Run bootstrapping
boot = Bootstrapper(fs, n_bootstraps=50, n_jobs=4, random_state=42, verbose=True)
boot.fit(X, y)

print(boot.results_)
print(boot.results_.shape)

# Aggregators
rank_agg = MeanRankAggregator().fit(boot.results_)               # rank-based (lower rank = better)
mean_agg = MeanAggregator().fit(boot.results_)                   # score-based mean
sum_agg = SumAggregator().fit(boot.results_)                     # score-based sum
borda_agg = BordaFromScoresAggregator().fit(boot.results_)       # Borda from scores (refactor name)

# Visualizations
viz = Visualizer()
viz.feature_frequency(boot.results_, n_features=X.shape[1], top_k=30)
viz.consensus_ranking(rank_agg.final_ranking_, top_k=15)
viz.stability_heatmap(boot.results_, n_features=X.shape[1], feature_names=col_names, cmap="Blues")

viz.compare_aggregators_heatmap({
    "RankAggregator": rank_agg.final_ranking_,
    "MeanAggregator": mean_agg.final_ranking_,
    "BordaAggregator": borda_agg.final_ranking_,
    "SumAggregator": sum_agg.final_ranking_
}, top_k=10, feature_names=col_names, annotate=True)

viz.cumulative_agreement_plot({
    "RankAggregator": rank_agg.final_ranking_,
    "MeanAggregator": mean_agg.final_ranking_
}, max_k=20, feature_names=col_names)

aggregator_results = {
    "RankAggregator": rank_agg.final_ranking_,
    "MeanAggregator": mean_agg.final_ranking_,
    "BordaAggregator": borda_agg.final_ranking_,
    "SumAggregator": sum_agg.final_ranking_
}

viz.topk_upset_plot(aggregator_results, top_k=10, feature_names=col_names)

