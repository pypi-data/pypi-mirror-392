import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

"""
clustering.py
------------------------------------------------------------
Final clustering utilities for the pipeline.

This module covers:
  (1) Running K-means clustering on a 2D embedding (e.g. UMAP).
  (2) Generating a publication-style scatter plot of the clusters.
"""

def kmeans_cluster(embedding_df, n_clusters, random_state=0):
    """
    Run K-means clustering on a low-dimensional embedding
    (e.g. UMAP coordinates).

    Parameters
    ----------
    embedding_df : pd.DataFrame
        Coordinate matrix (rows = samples, columns = features such as UMAP1/UMAP2).
    n_clusters : int
        Number of clusters (k).
    random_state : int, default=0
        Random seed for reproducibility.

    Returns
    -------
    labels : pd.Series
        Cluster assignment for each sample
        (index aligned to embedding_df.index).
    model : KMeans
        Fitted sklearn KMeans model.
    """
    km = KMeans(n_clusters=n_clusters, n_init="auto", random_state=random_state)
    lab = km.fit_predict(embedding_df.values)
    labels = pd.Series(lab, index=embedding_df.index, name="cluster")
    return labels, km


def plot_clusters(
    embedding_df,
    cluster_labels,
    title=None,
    save_path=None,
    point_size=20,
    alpha=0.8,
    cmap="tab20",
):
    """
    Create a 2D scatter plot of the embedding colored by cluster labels.

    Parameters
    ----------
    embedding_df : pd.DataFrame
        DataFrame with columns corresponding to embedding dimensions
        (e.g., ["UMAP1", "UMAP2"]).
        Index should match cluster_labels.index.
    cluster_labels : pd.Series
        Cluster assignment for each sample.
    title : str or None
        Title for the plot. If None, a default title will be used.
    save_path : str or None
        If provided, the figure will be saved to this path (e.g. "cluster_plot.png").
    point_size : int, default=20
        Marker size for scatter points.
    alpha : float, default=0.8
        Point transparency.
    cmap : str, default="tab20"
        Matplotlib colormap name.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure.
    ax : matplotlib.axes.Axes
        The created axes.
    """
    if title is None:
        title = "Final clustering"

    fig, ax = plt.subplots(figsize=(6, 5))
    sc = ax.scatter(
        embedding_df.iloc[:, 0],
        embedding_df.iloc[:, 1],
        c=cluster_labels.values,
        s=point_size,
        alpha=alpha,
        cmap=cmap,
    )
    ax.set_xlabel(embedding_df.columns[0])
    ax.set_ylabel(embedding_df.columns[1])
    ax.set_title(title)

    # optional legend-like color bar for clusters
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Cluster ID")

    plt.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=300)

    return fig, ax


def run_final_clustering(
    embedding_df,
    best_k,
    random_state=0,
    save_plot_path=None,
):
    """
    High-level helper to perform the final K-means clustering step
    after k has been selected.

    This is intended to be the last step of the pipeline, after:
      1. Embedding (UMAP) is computed.
      2. The optimal number of clusters (best_k) has been determined.

    Parameters
    ----------
    embedding_df : pd.DataFrame
        Low-dimensional embedding (e.g. UMAP coordinates).
        Rows = samples, columns = ["UMAP1", "UMAP2"] (or similar).
    best_k : int
        Chosen number of clusters.
    random_state : int, default=0
        Random seed for reproducibility.
    save_plot_path : str or None
        If provided, a scatter plot of the final clustering will
        be saved to this location.

    Returns
    -------
    output : dict
        {
            "labels": pd.Series,     # final cluster assignment per sample
            "k": int,                # best_k
            "model": KMeans,         # fitted KMeans model
            "plot_path": str or None # path where plot was saved
        }
    """
    labels, model = kmeans_cluster(
        embedding_df,
        n_clusters=best_k,
        random_state=random_state,
    )

    # produce / optionally save a final visualization
    plot_clusters(
        embedding_df,
        labels,
        title=f"K-means clustering (k={best_k})",
        save_path=save_plot_path,
    )

    out = {
        "labels": labels,
        "k": best_k,
        "model": model,
        "plot_path": save_plot_path,
    }
    return out
