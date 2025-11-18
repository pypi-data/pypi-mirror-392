import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
normalization.py
------------------------------------------------------------
Housekeeping gene (HKG)-based normalization utilities.

This module provides:
1. Stability scoring of candidate housekeeping genes across groups.
2. Selection of the most stable HKGs.
3. Sample-wise normalization using the selected HKGs.
"""


def score_hkg_stability(expr_df, meta_df, hkg_list, group_col="group"):
    """
    Compute stability metrics for candidate housekeeping genes (HKG)
    across biological or technical groups.

    For each gene within each group, dispersion is quantified using:
    - MFC: max/min fold change (robust dynamic range)
    - MAD: median absolute deviation
    - CV : coefficient of variation
    We also compute trimmed versions (excluding the min and max sample)
    when >=3 samples are available.

    Args:
        expr_df (pd.DataFrame):
            Expression matrix with rows = genes/transcripts,
            columns = samples.
        meta_df (pd.DataFrame):
            Metadata. Must contain a column named 'sample' (sample IDs)
            and a grouping column such as 'group' or 'group_disease'.
        hkg_list (list[str]):
            Candidate housekeeping gene IDs (must match expr_df.index).
        group_col (str):
            Column in meta_df defining the group identity.

    Returns:
        pd.DataFrame:
            Long-format table with per-(group,gene) stability metrics:
            ["group","gene","MFC_trim","MAD_trim","CV_trim"]
    """
    # subset to candidate HKGs only
    sub_expr = expr_df.loc[expr_df.index.intersection(hkg_list)].copy()
    results = []

    for group, meta_sub in meta_df.groupby(group_col):
        group_samples = meta_sub["sample"].tolist()
        # restrict expression to samples in this group
        group_mat = sub_expr[group_samples]

        for gene in group_mat.index:
            values = group_mat.loc[gene].sort_values()
            n = len(values)

            mean_val = values.mean()
            min_val = values.min()
            max_val = values.max()

            # basic dispersion measures
            mfc = max_val / (min_val + 1e-5)
            mad = (values - values.median()).abs().median()
            cv = values.std(ddof=0) / (mean_val + 1e-5)

            # trimmed versions (drop min and max if possible)
            if n > 2:
                trimmed = values.iloc[1:-1]
                mean_trim = trimmed.mean()
                min_trim = trimmed.min()
                max_trim = trimmed.max()

                mfc_trim = max_trim / (min_trim + 1e-5)
                mad_trim = (trimmed - trimmed.median()).abs().median()
                cv_trim = trimmed.std(ddof=0) / (mean_trim + 1e-5)
            else:
                mfc_trim, mad_trim, cv_trim = np.nan, np.nan, np.nan

            results.append(
                {
                    "group": group,
                    "gene": gene,
                    "MFC_trim": mfc_trim,
                    "MAD_trim": mad_trim,
                    "CV_trim": cv_trim,
                }
            )

    return pd.DataFrame(results)

# ------------------------------------------------------------
# Default housekeeping gene list (20 ENST transcripts)
# Used if user does not manually provide hkg_list
# ------------------------------------------------------------
DEFAULT_HKG_ENST = [
    "ENST00000309311","ENST00000382581","ENST00000265062","ENST00000311481",
    "ENST00000356674","ENST00000334478","ENST00000577035","ENST00000328024",
    "ENST00000375882","ENST00000418115","ENST00000353555","ENST00000303577",
    "ENST00000546120","ENST00000371646","ENST00000292807","ENST00000224073",
    "ENST00000327141","ENST00000435120","ENST00000394936","ENST00000395850",
]

def select_stable_hkg(expr_df, meta_df, hkg_list, group_col="group", top_n=3):
    """
    Rank candidate housekeeping genes by cross-group stability and select the top N.
    If hkg_list is not provided, uses DEFAULT_HKG_ENST (20 transcripts).

    We aggregate (mean across groups) the trimmed dispersion metrics
    (MFC_trim, MAD_trim, CV_trim). Each metric is z-score normalized.
    The sum of z-scores is used as a composite stability score.
    Genes with the lowest composite score are considered most stable.

    Args:
        expr_df (pd.DataFrame):
            Expression matrix (genes × samples).
        meta_df (pd.DataFrame):
            Metadata with 'sample' and grouping info.
        hkg_list (list[str]):
            Candidate HKG IDs.
        group_col (str):
            Column defining groups in meta_df.
        top_n (int):
            Number of HKGs to return.

    Returns:
        (list[str], pd.DataFrame):
            top_genes:
                List of selected stable HKG IDs.
            ranking_df:
                DataFrame of all genes with stability_score and z-scores.

    """
    stability = score_hkg_stability(expr_df, meta_df, hkg_list, group_col)

    # aggregate metrics across groups
    agg = (
        stability.groupby("gene")
        .agg(
            {
                "MFC_trim": "mean",
                "MAD_trim": "mean",
                "CV_trim": "mean",
            }
        )
    )

    tmp = agg.copy()
    for col in ["MFC_trim", "MAD_trim", "CV_trim"]:
        # lower is better, so direct z-score is fine;
        # we will sum them and then sort ascending
        tmp[col + "_z"] = (tmp[col] - tmp[col].mean()) / (
            tmp[col].std(ddof=0) + 1e-9
        )

    tmp["stability_score"] = (
        tmp["MFC_trim_z"] + tmp["MAD_trim_z"] + tmp["CV_trim_z"]
    )

    tmp = tmp.sort_values("stability_score", ascending=True)

    top_genes = list(tmp.index[:top_n])
    return top_genes, tmp


def normalize_by_hkg(expr_df, hkg_genes):
    """
    Normalize per-sample expression using the geometric mean of selected HKGs.

    The geometric mean expression of the chosen HKGs is computed for
    each sample. Each sample is scaled so that its HKG geometric mean
    matches the global median HKG level. This produces a simple
    multiplicative normalization factor per sample.

    Args:
        expr_df (pd.DataFrame):
            Expression matrix (genes × samples).
        hkg_genes (list[str]):
            List of stable housekeeping genes.

    Returns:
        (pd.DataFrame, pd.Series):
            expr_norm:
                Normalized expression matrix (same shape as expr_df).
            scale_factor:
                Per-sample scaling factor that was applied.
    """
    eps = 1e-5
    hkg_expr = expr_df.loc[hkg_genes]

    # geometric mean per sample
    geom_mean_per_sample = np.exp(
        np.mean(np.log(hkg_expr + eps), axis=0)
    )

    # global reference = median geometric mean
    target = np.median(geom_mean_per_sample)

    scale_factor = target / (geom_mean_per_sample + eps)

    expr_norm = expr_df * scale_factor

    return (
        expr_norm,
        pd.Series(scale_factor, index=expr_df.columns, name="scale_factor"),
    )

def plot_pre_post_normalization_heatmap(
    expr_before,
    expr_after,
    sample_order=None,
    gene_subset=None,
    vmax=None,
    top_n_genes=50,
    save_path=None,
    title_before="raw",
    title_after="HKG-normalized",
):
    """
    Visualize expression before vs after HKG normalization as side-by-side heatmaps.

    The figure shows two heatmaps (raw vs normalized) using the genes with
    the largest absolute change in mean expression across samples.

    Parameters
    ----------
    expr_before : pd.DataFrame
        Expression matrix before normalization.
        Rows = genes, columns = samples.
    expr_after : pd.DataFrame
        Expression matrix after normalization.
        Must have the same index/columns as expr_before.
    sample_order : list[str] or None
        Optional order of samples (columns). If None, use expr_before.columns.
    gene_subset : list[str] or None
        Optional list of genes to plot (e.g. housekeeping genes or marker genes).
        If None, automatically select top_n_genes genes with largest mean shift.
    vmax : float or None
        Upper clip for color scale. If None, uses 95th percentile of expr_before.
        The same vmax is applied to expr_after for comparability.
    top_n_genes : int
        Number of most-shifted genes to include when gene_subset is not provided.
    save_path : str or None
        If given, save the figure to this path (e.g. "norm_heatmap.png").
    title_before : str
        Title for the left panel.
    title_after : str
        Title for the right panel.

    Returns
    -------
    fig, axes : matplotlib Figure and Axes
    """

    # 1. align rows (genes) then columns (samples)
    expr_before, expr_after = expr_before.align(expr_after, join="inner", axis=0)
    expr_before, expr_after = expr_before.align(expr_after, join="inner", axis=1)

    if sample_order is None:
        sample_order = list(expr_before.columns)

    # 2. choose which genes to show
    if gene_subset is None:
        # absolute change in mean expression across samples
        delta = (expr_after.mean(axis=1) - expr_before.mean(axis=1)).abs()

        # pick top N (but don't crash if gene count < N)
        n_pick = min(top_n_genes, len(delta))
        gene_subset = delta.nlargest(n_pick).index

    sub_before = expr_before.loc[gene_subset, sample_order]
    sub_after  = expr_after.loc[gene_subset, sample_order]

    # 3. color scale
    if vmax is None:
        vmax = np.percentile(sub_before.values, 95)

    # let vmin be the global min so we don't artificially clamp negatives to 0
    vmin = min(sub_before.values.min(), sub_after.values.min())

    # 4. plot
    fig, axes = plt.subplots(1, 2, figsize=(10, 6), sharey=True)

    im0 = axes[0].imshow(sub_before.values, aspect="auto", vmin=vmin, vmax=vmax)
    axes[0].set_title(title_before)
    axes[0].set_xlabel("samples")
    axes[0].set_ylabel("genes")

    im1 = axes[1].imshow(sub_after.values, aspect="auto", vmin=vmin, vmax=vmax)
    axes[1].set_title(title_after)
    axes[1].set_xlabel("samples")

    # 5. shared colorbar
    fig.subplots_adjust(right=0.87)
    cbar = fig.colorbar(im1, ax=axes.ravel().tolist(), shrink=0.6, location="right", pad=0.02)
    cbar.set_label("expression level")

    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig, axes


def compute_logFC_vs_matched_HC(
    expr_df,
    meta_df,
    disease_col="disease",
    label_col="label",
    control_name="HC",
    sample_col="sample",
    pseudocount=1e-5,
    save_path=None,
):
    """
    Compute per-sample log fold change (logFC) for each disease sample
    relative to matched controls.

    Matching rule:
    - For a given disease D (e.g. "RA"), collect all samples with disease_col == D.
    - Extract their subtype labels from label_col (e.g. "RA/seropos+", "RA/serop-").
    - Among control_name samples (e.g. HC), keep only those whose label_col
      contains any of those subtype tokens (split by '/').
    - Compute mean expression across the matched controls.
    - logFC(sample) = log2(sample + pseudocount) - log2(mean_control + pseudocount).

    Parameters
    ----------
    expr_df : pd.DataFrame
        Expression matrix with rows = genes, columns = samples.
    meta_df : pd.DataFrame
        Metadata dataframe. Must include:
        - sample_col (sample ID)
        - disease_col (disease label, e.g. "HC", "RA", ...)
        - label_col (subtype / matching key)
    disease_col : str
        Column in meta_df describing disease status.
    label_col : str
        Column in meta_df describing subtype/phenotype.
        Used for matching controls.
    control_name : str
        Value in disease_col considered control (e.g. "HC").
    sample_col : str
        Column in meta_df that matches expr_df columns.
    pseudocount : float
        Stability constant added before log2.
    save_path : str or None
        If provided, save the resulting logFC_df to this CSV path.

    Returns
    -------
    logFC_df : pd.DataFrame
        Rows = genes, columns = disease samples.
        Each column is that sample's logFC vs its matched controls.
    """

    # 1. align meta_df to expression columns
    common_samples = meta_df[sample_col][meta_df[sample_col].isin(expr_df.columns)]
    meta_sub = meta_df[meta_df[sample_col].isin(common_samples)].set_index(sample_col)
    expr_sub = expr_df[common_samples]

    # 2. init output
    logFC_df = pd.DataFrame(index=expr_sub.index)

    # 3. list all non-control diseases
    disease_list = [
        d for d in meta_sub[disease_col].unique()
        if d != control_name
    ]

    for disease in disease_list:
        # samples of this disease
        disease_samples = meta_sub.index[meta_sub[disease_col] == disease].tolist()
        disease_labels = meta_sub.loc[disease_samples, label_col].astype(str).unique()

        # pool of potential controls
        ctrl_pool = meta_sub[meta_sub[disease_col] == control_name]

        # select only controls whose label matches any subtype token
        matched_ctrl_idx = ctrl_pool[
            ctrl_pool[label_col].astype(str).apply(
                lambda lab: any(
                    token in lab.split("/")
                    for token in disease_labels
                )
            )
        ].index.tolist()

        if len(matched_ctrl_idx) == 0:
            print(f"[Warning] No {control_name} match for disease={disease}")
            continue

        # 4. mean control profile in log space
        ctrl_avg_expr = np.log2(
            expr_sub[matched_ctrl_idx].mean(axis=1) + pseudocount
        )

        # 5. logFC for each disease sample
        for sample in disease_samples:
            sample_expr = np.log2(expr_sub[sample] + pseudocount)
            logFC_df[sample] = sample_expr - ctrl_avg_expr

    # 6. optional save
    if save_path is not None:
        logFC_df.to_csv(save_path)

    return logFC_df
