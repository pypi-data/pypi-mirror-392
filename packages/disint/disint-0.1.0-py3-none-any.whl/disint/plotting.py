import matplotlib.pyplot as plt
import numpy as np

"""
plotting.py
------------------------------------------------------------
Basic visualization helpers for embeddings and clusters.
"""


def plot_clusters_2d(
    embedding_df,
    labels,
    figsize=(6, 5),
    alpha=0.8,
    s=20,
    save_path=None,
):
    """
    Scatter plot of a 2D embedding (e.g. UMAP1 vs UMAP2),
    colored by cluster label.
    """
    if hasattr(labels, "reindex"):
        lbl = labels.reindex(embedding_df.index)
    else:
        lbl = np.asarray(labels)

    x_col, y_col = embedding_df.columns[:2]

    fig, ax = plt.subplots(figsize=figsize)
    for lab in np.unique(lbl):
        mask = (lbl == lab)
        ax.scatter(
            embedding_df.loc[mask, x_col],
            embedding_df.loc[mask, y_col],
            label=str(lab),
            s=s,
            alpha=alpha,
            edgecolors="black",
            linewidths=0.3,
        )

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.legend(
        title="cluster",
        markerscale=1.5,
        fontsize=8,
        bbox_to_anchor=(1.02, 1), 
        loc="upper left",
        borderaxespad=0.0,
    )

    fig.subplots_adjust(right=0.8, bottom=0.15)

    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig, ax


def plot_groups_2d(
    embedding_df,
    group_series,
    figsize=(6, 5),
    alpha=0.8,
    s=20,
    save_path=None,
    title=None,
):
    """
    Scatter plot of a 2D embedding (e.g. UMAP1 vs UMAP2),
    colored by a provided grouping annotation (e.g. disease, Cell_Type).
    """
    grp = group_series.reindex(embedding_df.index).astype(str)
    x_col, y_col = embedding_df.columns[:2]

    fig, ax = plt.subplots(figsize=figsize)

    for val in np.unique(grp):
        mask = (grp == val)
        ax.scatter(
            embedding_df.loc[mask, x_col],
            embedding_df.loc[mask, y_col],
            label=str(val),
            s=s,
            alpha=alpha,
            edgecolors="black",
            linewidths=0.3,
        )

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)

    if title is not None:
        ax.set_title(title)

    ax.legend(
        title="group",
        markerscale=1.5,
        fontsize=8,
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        borderaxespad=0.0,
    )

    fig.subplots_adjust(right=0.8, bottom=0.15)

    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig, ax
