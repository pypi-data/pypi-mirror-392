import os
import pandas as pd
from .embedding import fit_embedding_and_clusters
from .plotting import plot_clusters_2d, plot_groups_2d
import json


"""
io_utils.py
------------------------------------------------------------
High-level helpers for:
1. Loading expression + metadata from CSV files.
2. Running the full pipeline (PCA → UMAP → k selection → KMeans).
3. Saving results (coordinates, labels, metrics, figures).
"""


def load_expr_meta(expr_path, meta_path, sample_col="sample"):
    """
    Load expression and metadata tables from CSV files and align them.

    The function aligns samples between expr and meta. The expression
    matrix is expected to be genes × samples. The metadata table is
    expected to have a column indicating sample IDs (default "sample"),
    which will become its index.

    Args:
        expr_path (str):
            Path to expression CSV (rows = genes, cols = samples).
        meta_path (str):
            Path to metadata CSV.
        sample_col (str):
            Column in metadata that matches the expression columns.

    Returns:
        (pd.DataFrame, pd.DataFrame):
            expr_df:
                Expression matrix (genes × samples), subset/reordered so
                its columns match the aligned metadata index.
            meta_df:
                Metadata DataFrame indexed by sample ID.
    """
    expr_df = pd.read_csv(expr_path, index_col=0)
    meta_df = pd.read_csv(meta_path)

    if sample_col not in meta_df.columns:
        raise ValueError(
            f"Metadata must contain column '{sample_col}' to match samples."
        )

    # set index to sample ID
    meta_df = meta_df.set_index(sample_col)

    # intersect and align
    common_samples = [s for s in expr_df.columns if s in meta_df.index]
    expr_df = expr_df[common_samples]
    meta_df = meta_df.loc[common_samples]

    # also store the sample id explicitly for convenience in downstream steps
    meta_df["sample"] = meta_df.index

    return expr_df, meta_df


def run_full_pipeline(
    expr_df,
    meta_df=None,
    label_col=None,
    use_pca=True,
    pca_components=50,
    pca_scale=False,
    use_optuna=True,
    optuna_trials=50,
    optuna_k_provisional=10,
    random_state=0,
):
    """
    Thin wrapper around fit_embedding_and_clusters() to provide a stable
    top-level API for end users.

    Args:
        expr_df (pd.DataFrame):
            Rows = samples, columns = features (IMPORTANT: see note below).
            NOTE: If your expression matrix is genes × samples, you must
                  transpose before calling (expr_df.T).
        meta_df (pd.DataFrame or None):
            Metadata aligned to expr_df.index.
        label_col (str or None):
            Column in meta_df to guide supervised steps.
        use_pca, pca_components, pca_scale, use_optuna, optuna_trials,
        optuna_k_provisional, random_state:
            See fit_embedding_and_clusters().

    Returns:
        dict:
            Same structure as fit_embedding_and_clusters().
    """
    return fit_embedding_and_clusters(
        expr_df=expr_df,
        label_df=meta_df,
        label_col=label_col,
        use_pca=use_pca,
        pca_components=pca_components,
        pca_scale=pca_scale,
        use_optuna=use_optuna,
        optuna_trials=optuna_trials,
        optuna_k_provisional=optuna_k_provisional,
        manual_umap_params=None,
        random_state=random_state,
    )




def save_pipeline_outputs(
    result_dict,
    out_dir,
    meta_df=None,
    color_by_cols=None,
):
    """
    Save all outputs from fit_embedding_and_clusters().

    For each metric in result_dict["per_metric"], we create:
        <out_dir>/<metric_name>/
            umap_coordinates.csv
            cluster_labels.csv
            k_selection_scores.csv
            umap_clusters.png
            umap_by_<col>.png        (for each col in color_by_cols, if provided)
            umap_params.json         (Optuna best params: n_neighbors, min_dist, metric)

    We also write:
        <out_dir>/summary_metrics.csv     (one row per metric)
        <out_dir>/pca_coordinates.csv     (if PCA was computed)

    Parameters
    ----------
    result_dict : dict
        Output from fit_embedding_and_clusters().
        Must contain:
            - "pca_df"
            - "per_metric": dict keyed by metric name
              each value has:
                "umap_df"
                "umap_params"
                "final_k"
                "final_labels"
                "clustering_scores"
    out_dir : str
        Directory where results will be written.
    meta_df : pd.DataFrame or None
        Sample metadata aligned with result_dict indices.
    color_by_cols : list[str] or None
        Optional columns in meta_df to color UMAP by
        (ex: ["disease", "Cell_Type"]).
    """
    os.makedirs(out_dir, exist_ok=True)

    per_metric = result_dict["per_metric"]
    summary_rows = []

    # loop over each metric's result
    for metric_name, info in per_metric.items():
        metric_dir = os.path.join(out_dir, metric_name)
        os.makedirs(metric_dir, exist_ok=True)

        umap_df = info["umap_df"]                      # DataFrame (UMAP1/UMAP2)
        umap_params = info["umap_params"]              # dict with n_neighbors, min_dist, metric
        final_k = info["final_k"]                      # int
        final_labels = info["final_labels"]            # pd.Series
        clustering_scores = info["clustering_scores"]  # dict (silhouette, CH, DB)

        # 1. save UMAP coordinates
        umap_df.to_csv(os.path.join(metric_dir, "umap_coordinates.csv"))

        # 2. save cluster labels (+ k)
        lab_df = final_labels.to_frame(name="cluster")
        lab_df["k"] = final_k
        lab_df.to_csv(os.path.join(metric_dir, "cluster_labels.csv"))

        # 3. save clustering metrics (quality scores at the chosen k)
        pd.DataFrame([clustering_scores]).to_csv(
            os.path.join(metric_dir, "k_selection_scores.csv"),
            index=False,
        )

        # 4. plot UMAP colored by final KMeans clusters
        fig, ax = plot_clusters_2d(
            embedding_df=umap_df,
            labels=final_labels,
            save_path=os.path.join(metric_dir, "umap_clusters.png"),
        )
        # avoid figure accumulation in notebooks
        try:
            import matplotlib.pyplot as plt
            plt.close(fig)
        except Exception:
            pass

        # 4b. save k-selection curve if available
        if info.get("k_selection_plot", None) is not None:
            fig_k, ax_k = info["k_selection_plot"]
            try:
                fig_k.savefig(
                    os.path.join(metric_dir, "k_selection_plot.png"),
                    dpi=300,
                    bbox_inches="tight",
                )
                import matplotlib.pyplot as plt
                plt.close(fig_k)
            except Exception:
                pass

        # 5. optional: plot UMAP colored by metadata columns
        if meta_df is not None and color_by_cols is not None:
            for col in color_by_cols:
                if col in meta_df.columns:
                    fig2, ax2 = plot_groups_2d(
                        embedding_df=umap_df,
                        group_series=meta_df[col],
                        save_path=os.path.join(metric_dir, f"umap_by_{col}.png"),
                        title=f"{metric_name} UMAP by {col}",
                    )
                    try:
                        import matplotlib.pyplot as plt
                        plt.close(fig2)
                    except Exception:
                        pass

        # 6. save UMAP params from Optuna (reproducibility)
        with open(os.path.join(metric_dir, "umap_params.json"), "w") as f:
            json.dump(umap_params, f, indent=2)

        # 7. row for global summary
        row = {
            "metric": metric_name,
            "final_k": final_k,
        }
        # add silhouette / CH / DB to the summary row
        row.update(clustering_scores)
        # add core UMAP params so you can compare across metrics
        row.update({
            "umap_n_neighbors": umap_params.get("n_neighbors"),
            "umap_min_dist": umap_params.get("min_dist"),
        })
        summary_rows.append(row)

    # 8. write cross-metric summary table
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(
        os.path.join(out_dir, "summary_metrics.csv"),
        index=False,
    )

    # 9. (optional) save PCA coordinates at top level
    if result_dict.get("pca_df") is not None:
        result_dict["pca_df"].to_csv(
            os.path.join(out_dir, "pca_coordinates.csv")
        )

