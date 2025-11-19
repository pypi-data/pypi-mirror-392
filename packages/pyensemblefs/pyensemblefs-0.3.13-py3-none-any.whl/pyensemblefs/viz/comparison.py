
import numpy as np
import itertools
from upsetplot import UpSet, from_memberships
import matplotlib.pyplot as plt
import seaborn as sns
import os, matplotlib

if os.environ.get("MPLBACKEND") is None:
    matplotlib.use("Agg")


def compare_aggregators_heatmap(aggregator_results, top_k=20, feature_names=None,
                                filename=None, cmap=None, annotate=False):

    agg_names = list(aggregator_results.keys())
    n_agg = len(agg_names)
    n_features = len(aggregator_results[agg_names[0]])

    matrix = np.full((n_agg, n_features), np.nan)

    for i, name in enumerate(agg_names):
        arr = np.asarray(aggregator_results[name])
    
        order_pos = np.argsort(arr) 
        top_idx = np.argsort(arr)[:top_k]
        for pos, feat_idx in enumerate(top_idx, start=1):
            matrix[i, feat_idx] = pos

    plt.figure(figsize=(max(12, n_features * 0.3), n_agg * 0.6 + 2))
    sns.set(style="whitegrid")

    my_cmap = cmap if cmap is not None else sns.diverging_palette(250, 30, l=65, center="dark", as_cmap=True)

    ax = sns.heatmap(
        matrix, annot=False, cmap=my_cmap, cbar=True, linewidths=0.5, linecolor="gray"
    )

    if annotate:
        for i in range(n_agg):
            for j in range(n_features):
                if not np.isnan(matrix[i, j]):
                    ax.text(j + 0.5, i + 0.5, int(matrix[i, j]),
                            ha="center", va="center", color="white", fontsize=9)

    xticks = feature_names if feature_names is not None else np.arange(n_features)
    ax.set_xticks(np.arange(n_features) + 0.5)
    ax.set_xticklabels(xticks, rotation=90)

    ax.set_yticks(np.arange(n_agg) + 0.5)
    ax.set_yticklabels(agg_names, rotation=0)

    ax.set_xlabel("Features")
    ax.set_ylabel("Aggregator")
    ax.set_title("Aggregators Comparison: Feature Ranks in Original Order")
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()


def cumulative_agreement_plot(aggregator_results, max_k=50, feature_names=None, filename=None):
    agg_names = list(aggregator_results.keys())
    ks = np.arange(1, max_k + 1)
    agreement_fractions = []

    for k in ks:
        topk_sets = [set(np.argsort(aggregator_results[name])[:k]) for name in agg_names]
        shared = set.intersection(*topk_sets)
        agreement_fractions.append(len(shared) / k)

    plt.figure(figsize=(8, 5))
    plt.plot(ks, agreement_fractions, marker='o')
    plt.xlabel("Top-k features")
    plt.ylabel("Fraction of shared features")
    plt.title("Cumulative Agreement Across Aggregators")
    plt.ylim(0, 1.05)
    plt.grid(True)
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()


def pairwise_cumulative_agreement(aggregator_results, max_k=20, filename=None):
    agg_names = list(aggregator_results.keys())
    ks = np.arange(1, max_k + 1)

    plt.figure(figsize=(8, 5))
    for name1, name2 in itertools.combinations(agg_names, 2):
        agreement_fractions = []
        for k in ks:
            top1 = set(np.argsort(aggregator_results[name1])[:k])
            top2 = set(np.argsort(aggregator_results[name2])[:k])
            shared = top1.intersection(top2)
            agreement_fractions.append(len(shared) / k)
        plt.plot(ks, agreement_fractions, marker='o', label=f"{name1} vs {name2}")

    plt.xlabel("Top-k features")
    plt.ylabel("Fraction of shared features")
    plt.title("Pairwise Cumulative Agreement Across Aggregators")
    plt.ylim(0, 1.05)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()


def topk_upset_plot(aggregator_results, top_k=20, feature_names=None, filename=None):
    methods = list(aggregator_results.keys())
    n_features = len(aggregator_results[methods[0]])

    if feature_names is None:
        feature_names = [f"F{i}" for i in range(n_features)]

    memberships = []
    labels = []
    for i in range(n_features):
        present_in = [method for method in methods if i in np.argsort(aggregator_results[method])[:top_k]]
        if present_in:
            memberships.append(present_in)
            labels.append(feature_names[i])

    upset_data = from_memberships(memberships, data=labels)

    plt.figure(figsize=(10, 6))
    UpSet(upset_data, subset_size='count', show_counts=True).plot()
    plt.title(f"Top-{top_k} Feature Overlap Across Methods")
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()