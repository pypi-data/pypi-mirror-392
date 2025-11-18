import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
)

def _score_clustering(embedding_df, labels):
    X = embedding_df.values
    y = np.asarray(labels)

    sil = silhouette_score(X, y, metric="euclidean")
    ch = calinski_harabasz_score(X, y)
    db = davies_bouldin_score(X, y)

    return {
        "silhouette": sil,
        "calinski_harabasz": ch,
        "davies_bouldin": db,
    }


def select_best_k(
    embedding_df,
    candidate_k,
    random_state=0,
    selection_metric="consensus",
    plot=True,
    save_path=None,
):
    """
    Evaluate multiple candidate k values for K-means on a fixed embedding
    (e.g. UMAP), and select the best k.

    Parameters
    ----------
    embedding_df : pd.DataFrame
        Low-dimensional coordinates (rows = samples, cols = e.g. ["UMAP1","UMAP2"]).
    candidate_k : iterable of int
        Values of k (number of clusters) to evaluate, e.g. range(2, 11).
    random_state : int, default=0
        Random seed for reproducibility.
    selection_metric : {"consensus", "silhouette", "calinski_harabasz", "ch",
                        "davies_bouldin", "db"}, default="consensus"
        Criterion used to pick the final k.
        - "consensus": maximize (silhouette, calinski_harabasz, -davies_bouldin)
        - "silhouette": maximize silhouette only
        - "calinski_harabasz"/"ch": maximize CH only
        - "davies_bouldin"/"db": minimize DB only
    plot : bool, default=False
        If True, generate a summary plot of each metric vs k.
    save_path : str or None
        If provided and plot=True, save the plot to this path (e.g. "k_scan.png").

    Returns
    -------
    result : dict
        {
            "best_k": int,
            "labels": pd.Series,
            "scores": dict,           # scores for best_k
            "all_results": list[dict] # [{'k':k, 'labels':..., 'scores':...}, ...]
        }
    """

    all_results = []

    # 1️⃣ Sweep over all k and compute metrics
    for k in candidate_k:
        km = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
        lab = km.fit_predict(embedding_df.values)
        labels_series = pd.Series(lab, index=embedding_df.index, name="cluster")
        scores = _score_clustering(embedding_df, labels_series)
        all_results.append({
            "k": k,
            "labels": labels_series,
            "scores": scores,
        })

    # 2️⃣ Choose best k according to selection_metric
    def score_key(item):
        s = item["scores"]
        if selection_metric == "consensus":
            return (s["silhouette"], s["calinski_harabasz"], -s["davies_bouldin"])
        elif selection_metric == "silhouette":
            return (s["silhouette"],)
        elif selection_metric in ("calinski_harabasz", "ch"):
            return (s["calinski_harabasz"],)
        elif selection_metric in ("davies_bouldin", "db"):
            return (-s["davies_bouldin"],)
        else:
            raise ValueError(
                f"Unknown selection_metric='{selection_metric}'. "
                "Use 'consensus', 'silhouette', 'calinski_harabasz', 'ch', 'davies_bouldin', or 'db'."
            )

    best_item = max(all_results, key=score_key)

    # 3️⃣ Optional plot
    if plot:
        ks = [item["k"] for item in all_results]
        sil_vals = np.array([item["scores"]["silhouette"] for item in all_results], dtype=float)
        ch_vals  = np.array([item["scores"]["calinski_harabasz"] for item in all_results], dtype=float)
        db_vals  = np.array([item["scores"]["davies_bouldin"] for item in all_results], dtype=float)

        # Normalize to 0–1, unify direction (higher = better)
        sil_n = (sil_vals - sil_vals.min()) / (sil_vals.max() - sil_vals.min() + 1e-12)
        ch_n  = (ch_vals  - ch_vals.min())  / (ch_vals.max()  - ch_vals.min()  + 1e-12)
        db_inv = -db_vals
        db_n = (db_inv - db_inv.min()) / (db_inv.max() - db_inv.min() + 1e-12)

        combined = (sil_n + ch_n + db_n) / 3.0

        plt.figure(figsize=(6, 4))
        plt.plot(ks, sil_n, marker="o", label="Silhouette (norm.)")
        plt.plot(ks, ch_n, marker="s", label="Calinski–Harabasz (norm.)")
        plt.plot(ks, db_n, marker="^", label="Davies–Bouldin (norm.)")
        plt.plot(ks, combined, "k-", linewidth=2, label="Combined score")

        # Vertical line color depends on chosen metric
        color_map = {
            "silhouette": "tab:blue",
            "calinski_harabasz": "tab:orange",
            "ch": "tab:orange",
            "davies_bouldin": "tab:green",
            "db": "tab:green",
            "consensus": "black",
        }
        line_color = color_map.get(selection_metric, "tab:blue")

        plt.axvline(
            best_item["k"],
            linestyle="--",
            linewidth=1,
            color=line_color,
            label=f"selected k={best_item['k']} ({selection_metric})"
        )

        plt.xlabel("Number of clusters (k)")
        plt.ylabel("Normalized score (0–1)")
        plt.title(f"Clustering quality across k ({embedding_df.attrs.get('metric', 'unspecified')})")
        plt.legend(fontsize=8)
        plt.tight_layout()

        if save_path is not None:
            plt.savefig(save_path, dpi=300)

    return {
        "best_k": best_item["k"],
        "labels": best_item["labels"],
        "scores": best_item["scores"],
        "all_results": all_results,
    }
