import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import umap
from disint.metrics import select_best_k

"""
embedding.py
------------------------------------------------------------
Dimensionality reduction and clustering utilities:

1. PCA projection
2. UMAP embedding
3. Optuna-based UMAP hyperparameter tuning
   - run per metric (euclidean / manhattan / canberra / cosine ...)
   - keep all metrics instead of discarding non-winners
4. Final clustering on each UMAP:
   - automatic k selection
   - KMeans clustering
"""


def run_pca(
    expr_df,
    n_components=50,
    scale=False,
    random_state=0,
):
    """
    Run PCA on a samples × features matrix.

    Args:
        expr_df (pd.DataFrame):
            Rows = samples, columns = features.
        n_components (int):
            Number of PCs to keep.
        scale (bool):
            If True, z-normalize each feature before PCA.
        random_state (int):
            Random seed.

    Returns:
        (pd.DataFrame, PCA):
            pca_df:
                DataFrame of PC scores (samples × n_components).
            pca_model:
                Fitted PCA object.
    """
    X = expr_df.values.astype(float)

    if scale:
        mean_ = X.mean(axis=0, keepdims=True)
        std_ = X.std(axis=0, keepdims=True) + 1e-9
        X = (X - mean_) / std_

    pca_model = PCA(n_components=n_components, random_state=random_state)
    X_pca = pca_model.fit_transform(X)

    cols = [f"PC{i+1}" for i in range(X_pca.shape[1])]
    pca_df = pd.DataFrame(X_pca, index=expr_df.index, columns=cols)

    return pca_df, pca_model


def run_umap(
    data_df,
    n_neighbors=15,
    min_dist=0.1,
    metric="euclidean",
    n_components=2,
    random_state=0,
    return_model=False,
):
    """
    Run UMAP on a samples × features matrix.

    Args:
        data_df (pd.DataFrame):
            Rows = samples, columns = features.
        n_neighbors (int):
            UMAP n_neighbors.
        min_dist (float):
            UMAP min_dist.
        metric (str):
            UMAP distance metric.
        n_components (int):
            Output dimensionality (2 for visualization).
        random_state (int):
            Random seed.
        return_model (bool):
            If True, also return the fitted UMAP reducer.

    Returns:
        pd.DataFrame or (pd.DataFrame, umap.UMAP):
            umap_df:
                DataFrame with columns ["UMAP1","UMAP2", ...].
    """
    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        n_components=n_components,
        random_state=random_state,
    )
    emb = reducer.fit_transform(data_df.values.astype(float))
    cols = [f"UMAP{i+1}" for i in range(emb.shape[1])]
    umap_df = pd.DataFrame(emb, index=data_df.index, columns=cols)

    if return_model:
        return umap_df, reducer
    return umap_df


def evaluate_umap_for_clustering_quality(
    embedding_df,
    labels,
    metric_name="silhouette",
):
    """
    Evaluate how well an embedding separates given labels.

    Currently supports silhouette only.

    Args:
        embedding_df (pd.DataFrame):
            Low-dimensional coordinates (rows = samples).
        labels (array-like or pd.Series):
            Class / cluster labels aligned with embedding_df.index.
        metric_name (str):
            Only "silhouette" is implemented.

    Returns:
        float: silhouette score (higher is better).
    """
    if metric_name != "silhouette":
        raise ValueError("Only silhouette is supported in this version.")
    return silhouette_score(
        embedding_df.values,
        np.asarray(labels),
        metric="euclidean",
    )


def _silhouette_for_trial_embedding(
    emb,
    y_true,
    k_provisional,
    random_state,
):
    """
    Internal helper:
    Given a 2D embedding 'emb' (numpy array of shape n_samples × 2),
    compute a silhouette score.

    If y_true is provided, use those labels (supervised score).
    Otherwise run provisional KMeans(k_provisional) on emb and use those
    labels (unsupervised fallback).
    """
    if y_true is not None:
        trial_labels = y_true
    else:
        km = KMeans(
            n_clusters=k_provisional,
            n_init="auto",
            random_state=random_state,
        )
        trial_labels = km.fit_predict(emb)

    return silhouette_score(
        emb,
        np.asarray(trial_labels),
        metric="euclidean",
    ), trial_labels


def tune_umap_hyperparams_optuna_single_metric(
    data_df,
    metric,
    k_provisional=10,
    n_trials=50,
    random_state=0,
    n_neighbors_range=(5, 120),
    min_dist_range=(0.01, 0.8),
    label_df=None,
    label_col=None,
):
    """
    Run Optuna to optimize UMAP hyperparameters for ONE fixed metric.

    For each trial:
        - sample n_neighbors and min_dist
        - run UMAP (2D) with the given metric
        - compute a silhouette-based separation score

    If label_df / label_col is provided, we score using those biological
    labels directly (supervised). Otherwise we perform provisional KMeans
    with k_provisional on the embedding and score that (unsupervised fallback).

    Args:
        data_df (pd.DataFrame):
            Rows = samples, columns = features (often PCA output).
            Index must align with label_df if supervision is used.
        metric (str):
            UMAP distance metric to optimize ("euclidean", "manhattan", etc.).
        k_provisional (int):
            Provisional number of clusters for unsupervised silhouette.
        n_trials (int):
            Number of Optuna trials for this metric.
        random_state (int):
            Random seed.
        n_neighbors_range (tuple[int,int]):
            Range for UMAP n_neighbors.
        min_dist_range (tuple[float,float]):
            Range for UMAP min_dist.
        label_df (pd.DataFrame or None):
            Optional metadata DataFrame.
        label_col (str or None):
            Column to use as class labels for supervised silhouette.

    Returns:
        dict:
            {
                "best_params": {
                    "n_neighbors": int,
                    "min_dist": float,
                    "metric": str
                },
                "best_score": float,
                "umap_df": pd.DataFrame,          # 2D embedding of best trial
                "labels_provisional": pd.Series   # labels used for scoring best trial
            }

    Notes:
        Requires `optuna`.
    """
    try:
        import optuna
    except ImportError as e:
        raise ImportError(
            "Optuna is required for tune_umap_hyperparams_optuna_single_metric(). "
            "Install optuna to enable automatic UMAP tuning."
        ) from e

    X = data_df.values.astype(float)

    # get supervision labels if provided
    y_true = None
    if label_df is not None and label_col and (label_col in label_df.columns):
        y_true = label_df.loc[data_df.index, label_col].astype(str)

    def objective(trial):
        n_neighbors = trial.suggest_int(
            "n_neighbors",
            n_neighbors_range[0],
            n_neighbors_range[1],
        )
        min_dist = trial.suggest_float(
            "min_dist",
            min_dist_range[0],
            min_dist_range[1],
        )

        reducer = umap.UMAP(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            metric=metric,  # <-- fixed metric
            n_components=2,
            random_state=random_state,
        )
        emb = reducer.fit_transform(X)

        score, _trial_labels = _silhouette_for_trial_embedding(
            emb=emb,
            y_true=y_true,
            k_provisional=k_provisional,
            random_state=random_state,
        )
        return score

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    # best params from Optuna
    best_trial_params = study.best_trial.params
    best_n_neighbors = best_trial_params["n_neighbors"]
    best_min_dist = best_trial_params["min_dist"]

    # retrain UMAP on best params
    best_reducer = umap.UMAP(
        n_neighbors=best_n_neighbors,
        min_dist=best_min_dist,
        metric=metric,
        n_components=2,
        random_state=random_state,
    )
    best_emb = best_reducer.fit_transform(X)

    # final labels (to store alongside embedding)
    best_score, best_labels_used = _silhouette_for_trial_embedding(
        emb=best_emb,
        y_true=y_true,
        k_provisional=k_provisional,
        random_state=random_state,
    )

    umap_df = pd.DataFrame(
        best_emb,
        index=data_df.index,
        columns=["UMAP1", "UMAP2"],
    )
    labels_series = pd.Series(
        best_labels_used,
        index=data_df.index,
        name="cluster_provisional",
    )

    return {
        "best_params": {
            "n_neighbors": best_n_neighbors,
            "min_dist": best_min_dist,
            "metric": metric,
        },
        "best_score": best_score,
        "umap_df": umap_df,
        "labels_provisional": labels_series,
    }


def tune_umap_hyperparams_optuna_multi(
    data_df,
    metric_list=("euclidean", "manhattan", "canberra", "cosine"),
    k_provisional=10,
    n_trials=50,
    random_state=0,
    n_neighbors_range=(5, 120),
    min_dist_range=(0.01, 0.8),
    label_df=None,
    label_col=None,
):
    """
    Run Optuna-based UMAP tuning independently for each metric in metric_list.

    We do NOT pick a single "winner".
    We keep the best solution for each metric.

    Args:
        data_df (pd.DataFrame):
            Rows = samples, columns = features (often PCA output).
        metric_list (iterable[str]):
            Distance metrics to evaluate.
        k_provisional (int):
            Provisional k used for unsupervised silhouette.
        n_trials (int):
            Optuna trials per metric.
        random_state (int):
            Random seed for UMAP / KMeans.
        n_neighbors_range (tuple[int,int]):
            Range for UMAP n_neighbors.
        min_dist_range (tuple[float,float]):
            Range for UMAP min_dist.
        label_df (pd.DataFrame or None):
            Metadata aligned to data_df.index.
        label_col (str or None):
            Column in label_df used as labels for supervised scoring.

    Returns:
        dict:
            keys: metric name (e.g. "manhattan")
            values: dict from tune_umap_hyperparams_optuna_single_metric(...)
    """
    out = {}
    for metric in metric_list:
        out[metric] = tune_umap_hyperparams_optuna_single_metric(
            data_df=data_df,
            metric=metric,
            k_provisional=k_provisional,
            n_trials=n_trials,
            random_state=random_state,
            n_neighbors_range=n_neighbors_range,
            min_dist_range=min_dist_range,
            label_df=label_df,
            label_col=label_col,
        )
    return out


def _select_best_k_for_embedding(
    embedding_df,
    random_state=0,
    selection_metric="consensus",
    label_df=None,
    label_col=None,
    k_upper_cap=50,
    fallback_upper=40,
):
    """
    Helper to choose k for KMeans on a given embedding.

    We define a candidate k range automatically:
    - If label_df/label_col given, we use the number of unique labels
      to bound k.
    - Otherwise we fall back to a heuristic upper bound.

    Then we call select_best_k() from metrics.py.
    We also request a plot so that the caller can save it later.
    """
    from .metrics import select_best_k

    # infer candidate k range
    if label_df is not None and label_col and (label_col in label_df.columns):
        groups = label_df.loc[embedding_df.index, label_col].astype(str)
        g_unique = groups.nunique()
        upper = min(max(g_unique, 2), k_upper_cap)
        k_range = range(2, upper + 1)
    else:
        upper = max(min(fallback_upper, k_upper_cap), 2)
        k_range = range(2, upper + 1)

    # ask select_best_k to generate the plot object for us
    k_sel = select_best_k(
        embedding_df=embedding_df,
        candidate_k=k_range,
        random_state=random_state,
        selection_metric=selection_metric,
        plot=True,          # ← changed from False
        save_path=None,     # we will save manually later
    )

    # select_best_k(...) should now have created a plot internally;
    # we want that figure/ax so we can save it per metric.
    # We'll support both patterns:
    # - either k_sel already includes it,
    # - or select_best_k returned (fig, ax) separately.
    k_plot = None
    if "plot_fig" in k_sel and "plot_ax" in k_sel:
        # if you decide to stash fig/ax inside k_sel in metrics.py
        k_plot = (k_sel["plot_fig"], k_sel["plot_ax"])
    elif "plot" in k_sel:
        # or maybe you stored them together
        k_plot = k_sel["plot"]
    # if neither exists, caller will just see k_plot = None and skip saving

    return k_sel, k_plot



def fit_embedding_and_clusters(
    expr_df,
    meta_df=None,
    label_col=None,
    use_pca=True,
    pca_components=50,
    pca_scale=False,
    random_state=0,
    metric_list=("euclidean", "manhattan", "canberra", "cosine"),
    optuna_trials=50,
    optuna_k_provisional=10,
    n_neighbors_range=(5, 120),
    min_dist_range=(0.01, 0.8),
    selection_metric="consensus",
):
    """
    Full pipeline:
    1. (optional) PCA
    2. For each metric in metric_list:
       - Optuna-tune UMAP hyperparameters for that metric
       - Get best UMAP embedding (2D)
       - Automatically select k
       - Run final KMeans
    3. Return results for ALL metrics

    Args:
        expr_df (pd.DataFrame):
            Rows = samples, columns = features.
        meta_df (pd.DataFrame or None):
            Metadata aligned to expr_df.index.
        label_col (str or None):
            Column in meta_df used as biological/clinical label.
            Used for supervised silhouette (UMAP tuning) and also to
            bound candidate k values.
        use_pca (bool):
            If True, run PCA before UMAP.
        pca_components (int):
            Number of PCs to keep.
        pca_scale (bool):
            If True, z-normalize features before PCA.
        random_state (int):
            Random seed.
        metric_list (iterable[str]):
            Distance metrics to evaluate independently.
        optuna_trials (int):
            Optuna trials per metric.
        optuna_k_provisional (int):
            Provisional k for unsupervised silhouette in tuning.
        n_neighbors_range (tuple[int,int]):
            Search range for UMAP n_neighbors.
        min_dist_range (tuple[float,float]):
            Search range for UMAP min_dist.

    Returns:
        dict:
            {
                "pca_df": pd.DataFrame or None,
                "per_metric": {
                    <metric_name>: {
                        "umap_df": pd.DataFrame,
                        "umap_params": dict,
                        "final_k": int,
                        "final_labels": pd.Series,
                        "clustering_scores": dict
                    },
                    ...
                }
            }

        Notes:
            - "umap_params" is the Optuna-best params for that metric
              (n_neighbors, min_dist, metric).
            - "clustering_scores" is the metric dict from select_best_k()
              (silhouette / Calinski–Harabasz / Davies–Bouldin) for final_k.
    """
    # Step 1. PCA or not
    if use_pca:
        pca_df, _pca_model = run_pca(
            expr_df,
            n_components=pca_components,
            scale=pca_scale,
            random_state=random_state,
        )
        base_features = pca_df
    else:
        pca_df = None
        base_features = expr_df

    # Step 2. UMAP tuning for all metrics
    tuned_all = tune_umap_hyperparams_optuna_multi(
        data_df=base_features,
        metric_list=metric_list,
        k_provisional=optuna_k_provisional,
        n_trials=optuna_trials,
        random_state=random_state,
        n_neighbors_range=n_neighbors_range,
        min_dist_range=min_dist_range,
        label_df=meta_df,
        label_col=label_col,
    )

    per_metric_results = {}

    # Step 3. For each metric's best embedding, choose k and run KMeans
    for metric_name, tuned in tuned_all.items():
        umap_df = tuned["umap_df"]
        umap_df.attrs["metric"] = metric_name
        umap_params = tuned["best_params"]

        # choose k + get plot
        k_sel, k_plot = _select_best_k_for_embedding(
            embedding_df=umap_df,
            random_state=random_state,
            selection_metric=selection_metric,
            label_df=meta_df,
            label_col=label_col,
            k_upper_cap=50,
            fallback_upper=40,
        )

        # Final labels for that k
        final_labels = k_sel["labels"]
        final_k = k_sel["best_k"]
        cluster_scores = k_sel["scores"]

        per_metric_results[metric_name] = {
            "umap_df": umap_df,
            "umap_params": umap_params,           # dict (n_neighbors, min_dist, metric)
            "final_k": final_k,                   # int
            "final_labels": final_labels,         # pd.Series
            "clustering_scores": cluster_scores,  # dict of silhouette/CH/DB
            "k_selection_plot": k_plot,           # (fig, ax) or None
        }

    return {
        "pca_df": pca_df,
        "per_metric": per_metric_results,
    }
