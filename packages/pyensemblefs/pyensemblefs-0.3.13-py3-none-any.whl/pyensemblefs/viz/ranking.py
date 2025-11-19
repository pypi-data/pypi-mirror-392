from __future__ import annotations
from typing import Sequence, Optional, Tuple
import os
import numpy as np
import matplotlib

if os.environ.get("MPLBACKEND") is None:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def consensus_ranking(ranking, top_k=20, feature_names=None, title="Consensus Ranking", filename=None):
    top_idx = np.asarray(ranking)[:top_k]
    ranks = np.arange(1, min(top_k, len(top_idx)) + 1)
    labels = (np.asarray(feature_names)[top_idx]
              if feature_names is not None
              else np.asarray([f"Feature {i}" for i in top_idx]))

    plt.figure(figsize=(10, 5))
    sns.barplot(
        x=ranks,
        y=labels,
        hue=labels,       
        palette="viridis",
        orient="h",
        legend=False
    )
    plt.title(title)
    plt.xlabel("Rank")
    plt.ylabel("Feature")
    plt.gca().invert_yaxis() 
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()


def plot_topk_frequency(
    feature_names: Sequence[str],
    frequencies: Sequence[float],
    title: Optional[str] = None,
    ref_threshold: Optional[float] = None,
    savepath: Optional[str] = None,
    figsize: Tuple[float, float] = (10, 6),
    rotate: int = 60,
    ylim: Tuple[float, float] | None = (0.0, 1.0),
    annotate: bool = False,
):

    names = list(map(str, feature_names))
    vals = np.asarray(frequencies, dtype=float).ravel()
    assert len(names) == len(vals), "feature_names and frequencies must have same length"

    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(names))
    ax.bar(x, vals)
    ax.set_xticks(x, names, rotation=rotate, ha="right")
    ax.set_ylabel("Selection frequency")
    if title:
        ax.set_title(title)
    if ylim is not None:
        ax.set_ylim(*ylim)
    if ref_threshold is not None:
        ax.axhline(ref_threshold, linestyle="--", linewidth=1.0)

    if annotate:
        for i, v in enumerate(vals):
            ax.text(i, v + 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=8)

    fig.tight_layout()

    if savepath:
        os.makedirs(os.path.dirname(savepath), exist_ok=True)
        fig.savefig(savepath, bbox_inches="tight")
        plt.close(fig)
        return None

    return fig, ax