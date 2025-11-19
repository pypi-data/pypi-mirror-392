import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os, matplotlib
if os.environ.get("MPLBACKEND") is None:
    matplotlib.use("Agg")


def _ensure_2d(array: np.ndarray) -> np.ndarray:
    array = np.asarray(array)
    if array.ndim == 1:
        return array.reshape(1, -1)
    return array


def _scores_to_binary_topk(scores_2d: np.ndarray, top_k: int) -> np.ndarray:
    B, p = scores_2d.shape
    mask = np.zeros_like(scores_2d, dtype=int)
    for b in range(B):
        top_idx = np.argsort(-scores_2d[b])[:top_k]
        mask[b, top_idx] = 1
    return mask


def feature_frequency(selected_or_scores, n_features, top_k=15, filename=None, as_fraction=True):
    mat = _ensure_2d(np.asarray(selected_or_scores))
    is_binary = np.array_equal(mat, mat.astype(bool))

    if is_binary:
        freq = mat.mean(axis=0) if as_fraction else mat.sum(axis=0)
        ylabel = "Selection Frequency (fraction of bootstraps)" if as_fraction else "Selection Count"
    else:
        sel = _scores_to_binary_topk(mat, top_k=top_k)
        freq = sel.mean(axis=0) if as_fraction else sel.sum(axis=0)
        ylabel = "Selection Frequency (fraction of bootstraps)" if as_fraction else "Selection Count"

    top_idx = np.argsort(-freq)[:top_k]
    labels = [f"Feature {i}" for i in top_idx]

    plt.figure(figsize=(8, 6))
    sns.barplot(
        x=freq[top_idx],
        y=labels,
        hue=labels,      
        palette="Blues_d",
        orient="h",
        dodge=False,
        legend=False
    )
    plt.xlabel(ylabel)
    plt.ylabel("Feature")
    plt.title(f"Top {top_k} Features by Selection Frequency")
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()


def stability_heatmap(selected_or_scores, n_features, top_k=10, title="Stability Heatmap",
                      feature_names=None, filename=None, cmap="viridis", annotate=False):

    if isinstance(selected_or_scores, list):
        # list of index arrays -> binary matrix
        matrix = np.zeros((len(selected_or_scores), n_features), dtype=int)
        for i, sel in enumerate(selected_or_scores):
            matrix[i, np.asarray(sel, dtype=int)] = 1
    else:
        mat = _ensure_2d(np.asarray(selected_or_scores))
        is_binary = np.array_equal(mat, mat.astype(bool))
        matrix = mat if is_binary else _scores_to_binary_topk(mat, top_k=top_k)

    xticks = feature_names if feature_names is not None else np.arange(n_features)

    plt.figure(figsize=(14, 6))
    sns.set(style="whitegrid")
    ax = sns.heatmap(
        matrix,
        cmap=cmap,
        cbar=True,
        linewidths=0.5,
        linecolor="gray",
        annot=annotate,
        square=False,
        xticklabels=xticks
    )
    plt.title(title, fontsize=14)
    plt.xlabel("Feature", fontsize=12)
    plt.ylabel("Bootstrap Sample", fontsize=12)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()


def stability_over_bootstraps(stability_scores, filename=None):
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(stability_scores) + 1), stability_scores, marker="o")
    plt.title("Stability vs. Number of Bootstraps")
    plt.xlabel("Number of Bootstraps")
    plt.ylabel("Stability")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()