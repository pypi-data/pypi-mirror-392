# disint · disease-integration

A reproducible and fully automated pipeline for large-scale disease transcriptome integration, normalization, dimensionality reduction, and clustering.

---

# Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Input File Format](#input-file-format)
- [Quick Start](#quick-start)
- [Advanced / Core Function Example](#advanced--core-function-example)
- [Output Structure](#output-structure)
- [Adaptive Behavior](#adaptive-behavior)
- [Note on version locking](#note-on-version-locking)
- [Citation](#citation)
- [License](#license)

---

# Overview

**disint** is a standardized, high-reproducibility Python pipeline designed for **multi-study disease transcriptomics**.  
It provides an end-to-end workflow — from raw or normalized expression matrices to publication-grade clustering and visualization —  
with a strong emphasis on **cross-dataset comparability**, **batch-aware normalization**, and **robust dimensionality reduction**.

Key capabilities include:

- **Housekeeping-gene–based normalization** using stability ranking across datasets  
  (default panel of 20 ENST transcripts or user-specified candidates)
- **Automatic log₂ fold-change estimation** vs. matched healthy controls within each dataset (e.g., each GSE)
- **PCA → UMAP embedding** with **metric-wise Optuna hyperparameter optimization**
- **Adaptive K-means clustering** with principled k-selection  
  (Silhouette, Calinski–Harabasz, Davies–Bouldin, and consensus scoring)
- **Visualization utilities** for normalization diagnostics and cluster interpretation
- Fully reproducible outputs including normalized matrices, logFC tables, embedding coordinates, clustering labels, and all intermediate optimization results

This package is designed for users working on:

- disease heterogeneity analysis  
- multi-dataset transcriptomic integration  
- drug repurposing candidate identification  
- high-dimensional biological data visualization  

By following the standardized pipeline, researchers can obtain **consistent**, **interpretable**, and **reproducible** results across heterogeneous datasets.

---



# Installation
```bash
pip install disint
```

# Input File Format
## 1. Expression Matrix (expr.csv)

| gene | sampleA | sampleB | sampleC | ... |
|----------|----------|----------|----------|----------|
| ENST00000309311 | 8.12 | 7.55 | 6.92 | ... |
| ENST00000382581 | 5.09 | 4.77 | 5.32 | ... |
| ... | ... | ... | ... |... |


- **Rows** represent genes or transcripts (e.g., Ensembl transcript IDs, gene symbols).  
- **Columns** represent samples and **must match** the `sample` column in the metadata file.  
- The **first column** is interpreted as the row index.  
- Values may be **raw counts** or **normalized counts**. 

> **Note:**  
> If your downstream goal is to compare gene-expression differences *across diseases* (e.g., for drug-repositioning analysis), then the input expression matrix should be a **logFC matrix**.  
> Each logFC value represents the *log₂ difference between an individual disease sample and its matched healthy control within the same group*.  
>   
> If you currently only have raw or normalized expression matrices, this package provides a fast built-in pipeline to compute logFC.  
> Please refer to [**“Compute log₂ fold-change vs matched controls”**](#compute-log2fc) for details.  
>   
> *Ensure that every group (e.g., each GSE dataset) contains at least one healthy-control sample (“HC”), as logFC cannot be computed otherwise.*


## 2 . Metadata (meta.csv)

| sample | disease | group | cell_type | ... |
|----------|----------|----------|----------|----------|
| sampleA | AD | GSE12345 | B_cell | ... |
| sampleB | HC | GSE12345 | B_cell | ... |
| sampleC | PD | GSE67890 | Mast_cell | ... |
| ... | ... | ... | ... |... |

- Must contain a **`sample` column** that exactly matches the expression matrix column names.  
- A **grouping column** (e.g., `group`, `disease`, `cell_type`) can be provided for supervised optimization and batch-aware processing.  
- Additional columns are optional and safely ignored during computation unless explicitly specified.

# Quick Start

```python
import pandas as pd
from disint import load_expr_meta
from disint.embedding import fit_embedding_and_clusters

expr_df, meta_df = load_expr_meta(
    expr_path="data/expr.csv",
    meta_path="data/meta.csv",
    sample_col="sample",
)

# fit_embedding_and_clusters expects rows = samples, cols = features
expr_for_embedding = expr_df.T

result = fit_embedding_and_clusters(
    expr_df=expr_for_embedding,
    meta_df=meta_df,

    label_col="disease",
    use_pca=True, 
    pca_components=50,
    pca_scale=False,

    random_state=0, 
    metric_list=("euclidean","manhattan","canberra","cosine"),

    optuna_trials=50,
    optuna_k_provisional=10,

    n_neighbors_range=(5,120),
    min_dist_range=(0.01,0.8),

    selection_metric="consensus",
)

save_pipeline_outputs(
    result_dict=result,
    out_dir="analysis_output",
    meta_df=meta_df,
    color_by_cols=["disease"], 
)
```

After running `fit_embedding_and_clusters`, you typically save results
per metric (euclidean / manhattan / canberra / cosine). 



A common layout is:
```text
analysis_multi_optuna/
├── euclidean/                  # or manhattan / canberra / cosine
│   ├── umap_coordinates.csv    # UMAP1 / UMAP2 for each sample
│   ├── cluster_labels.csv      # final KMeans label per sample + chosen k
│   ├── k_selection_scores.csv  # silhouette / CH / DB at the chosen k
│   ├── k_selection_plot.png    # per-metric results and plots
│   ├── umap_clusters.png       # UMAP colored by final KMeans clusters
│   ├── umap_by_disease.png     # optional: colored by metadata column
│   └── umap_params.json        # Optuna-selected UMAP parameters
```



# Advanced / Core Function Example

## Common Setup
```python
import pandas as pd
from disint import load_expr_meta

expr_df, meta_df = load_expr_meta(
    "data/expr.csv",
    "data/meta.csv",
    sample_col="sample",
)
```
### The following functional modules are available and can be used as needed.
- **Normalization** — [details](#1-housekeeping-gene-normalization--logfc)
- **Embedding** — [details](#2-pca-and-metric-wise-umap-tuning-optuna)
- **Clustering** — [details](#3-automatic-k-selection-and-final-clustering)
- **Visualization** — [details](#4-visualization)

## 1. Housekeeping-gene normalization & logFC

### (1) Select stable housekeeping genes
```python
from disint import (
    select_stable_hkg,
    normalize_by_hkg,
    compute_logFC_vs_matched_HC,
    plot_pre_post_normalization_heatmap,
    DEFAULT_HKG_ENST,
)

top_hkg, hkg_table = select_stable_hkg(
    expr_df=expr_df,
    meta_df=meta_df,
    hkg_list=DEFAULT_HKG_ENST,
    group_col="group",
    top_n=3,
)
```
### Notes
- **expr_df** must contain expression values where rows = transcript/genes and columns = samples.
- To use **DEFAULT_HKG_ENST**, the row index must consist of **Ensembl transcript IDs (e.g., ENSTxxxx)** **without version suffix**. For example:
  - `"ENST00000309311.5" → "ENST00000309311"`
  - You may preprocess using: `expr_df.index = expr_df.index.astype(str).str.split('.').str[0]`
- **meta_df** must contain:
  - **sample** — sample IDs matching `expr_df.columns`
  - **group** — batch / dataset / cohort label (used for within-group HKG stability evaluation)
  - **disease** — biological condition (later used for logFC)

### Outputs
- **hkg_table.csv** — stability metrics per candidate HKG (MFC_trim, MAD_trim, CV_trim per group)
- **top_hkg** — selected stable housekeeping genes

---

### (2) Normalize expression using selected housekeeping genes
```python
expr_norm, scale_factor = normalize_by_hkg(
    expr_df=expr_df,
    hkg_genes=top_hkg,
)
```
### Outputs
- **expression_normalized_by_HKG.csv** — HKG-normalized expression matrix (genes × samples)
- **HKG_scale_factor_per_sample.csv** — per-sample scaling factor

---

### (3) Visualize before/after normalization
```python
fig, axes = plot_pre_post_normalization_heatmap(
    expr_before=expr_df,
    expr_after=expr_norm,
    sample_order=meta_df["sample"],
    top_n_genes=50,
    save_path="norm_heatmap_top50.png",
    title_before="Raw",
    title_after="HKG-normalized",
)

fig.subplots_adjust(right=0.87)
```
### Output
- **norm_heatmap_top50.png** — side-by-side heatmap (raw vs normalized)

---

### (4) Compute log₂ fold-change vs matched controls
<a id="compute-log2fc"></a>
> **Note**  
> This function computes log₂ fold-change by comparing each disease sample with
> matched healthy-control samples *within the same group*.  
>  
> If you intend to compute logFC using this package, please ensure:  
> - the column specified by **`disease_col`** contains a label that represents healthy controls  
>   (default: `"HC"`, but this can be changed via `control_name`);  
> - the column specified by **`label_col`** defines groups within which matching is performed  
>   (e.g., GSE accession numbers, batch IDs, cohorts).  
>  
> During computation, each disease sample is compared **only to healthy-control samples from the same group**, ensuring batch-aware baseline matching.  

```python
logFC_df = compute_logFC_vs_matched_HC(
    expr_df=expr_norm,
    meta_df=meta_df,
    disease_col="disease",
    label_col="group",
    control_name="HC",
    sample_col="sample",
    pseudocount=1e-5,
)
logFC_df.to_csv("logFC_after_norm.csv")
```
### Output
- **logFC_after_norm.csv** — log₂FC values: disease vs matched HC within each group

---

### (5) Prepare matrix for embedding
```python
expr_for_embedding = expr_norm.T   # rows = samples, cols = genes
```

## 2. PCA and metric-wise UMAP tuning (Optuna)

### (1) PCA before UMAP (recommended for high-dimensional data)
```python
from disint.embedding import (
    run_pca,
    tune_umap_hyperparams_optuna_multi,
)

pca_df, pca_model = run_pca(
    expr_for_embedding,
    n_components=50,
    scale=False,
    random_state=0,
)
```

### Notes
- PCA is applied prior to UMAP to reduce noise and stabilize embedding in high-dimensional transcriptomic data.  
- `scale=False` preserves original expression magnitude, which may be biologically meaningful.  
- `pca_df` is used as input for metric-wise UMAP optimization.

---
### (2) Hyperparameter search for UMAP.
Each distance metric is tuned independently with Optuna.
```python

tuned_all = tune_umap_hyperparams_optuna_multi(
    data_df=pca_df,
    metric_list=("euclidean", "manhattan", "canberra", "cosine"),
    k_provisional=10,          # temporary k for internal silhouette scoring
    n_trials=50,               # Optuna trials per metric
    random_state=0,
    n_neighbors_range=(5, 120),
    min_dist_range=(0.01, 0.8),
    label_df=meta_df,
    label_col="disease",       # optional supervised guidance; can be None
)
```

### Notes
- UMAP hyperparameters are optimized independently for each metric because distance definitions strongly affect embedding structure.  
- `k_provisional` is only used for evaluating trial embeddings (silhouette score).  
- Supervised guidance (`label_col="disease"`) is optional and can be omitted for unsupervised analysis.  
- The result `tuned_all` stores optimized embeddings and parameters for all metrics.

---

### Example: get the best embedding for "manhattan"
```python
tuned = tuned_all["manhattan"]
umap_df = tuned["umap_df"]
best_params = tuned["best_params"] 
print(best_params)
```

### Notes
- `umap_df` provides the optimized UMAP coordinates for the chosen metric.  
- `best_params` contains the exact hyperparameters selected by Optuna, enabling reproducibility.  
- Any metric ("euclidean", "cosine", etc.) can be accessed similarly through `tuned_all`.

## 3. Automatic k selection and final clustering
### (1) Scan a range of k and select the consensus best k
```python
from disint.metrics import select_best_k

k_scan = select_best_k(
    embedding_df=umap_df,
    candidate_k=range(2, 41),
    random_state=0,
    selection_metric="consensus", # or "silhouette" / "ch" / "db"
    plot=True,
    save_path="k_scan.png",
)

best_k = k_scan["best_k"]
```
### Notes
- selection_metric=`"consensus"` aggregates multiple internal indices; alternatives are `"silhouette"`, `"ch"`, and `"db"`.
- `candidate_k` controls the cluster-number search range.
- During plotting, **all metrics are normalized to the range [0, 1]**, with **higher values consistently representing better cluster separation**.
- `plot=True` outputs the diagnostic figure `k_scan.png`.
- `best_k` stores the selected optimal number of clusters.

---
### (2) Final KMeans clustering with the chosen k
```python
from disint.clustering import kmeans_cluster

final = kmeans_cluster(
    embedding_df=umap_df,
    n_clusters=best_k,
    random_state=0,
)

cluster_labels = final["labels"] # pandas Series aligned with umap_df.index
```

### Notes
- `n_clusters=best_k` uses the optimal resolution derived from step (1).
- `cluster_labels` aligns with `umap_df.index` and is ready for downstream visualization/analysis.
- `random_state` ensures reproducibility.

## 4. Visualization
### (1) UMAP colored by final KMeans clusters
```python
from disint.plotting import (
    plot_clusters_2d,
    plot_groups_2d,
)

fig, ax = plot_clusters_2d(
    embedding_df=umap_df,
    labels=cluster_labels,
    save_path="umap_clusters.png",
)
```
### Notes
- `labels` must be indexed identically to `umap_df.index`.
- Additional keyword args (e.g., `s`, `alpha`, `legend`) can be passed through to control aesthetics.
- When `save_path` is provided, the figure is written to disk and the Matplotlib figure/axis objects are also returned.

---
### (2) UMAP colored by metadata annotation (e.g., disease state)
```python
fig2, ax2 = plot_groups_2d(
    embedding_df=umap_df,
    group_series=meta_df["disease"],
    save_path="umap_by_disease.png",
    title="UMAP colored by disease",
)
```
### Notes
- `group_series` must align with `umap_df.index`; a Pandas `Categorical` can be used to control legend order.
- `title` is optional; omit or customize as needed.
- Use consistent color/marker schemes across figures for comparability.

## Key Parameters

| Parameter | Description |
|----------|-------------|
| **expr_df** | Expression matrix (genes × samples). After loading, transpose so rows = samples. |
| **meta_df** | Metadata indexed by sample. Must include grouping variables. |
| **label_col** | Column in `meta_df` for biological grouping (e.g., `disease`). Used for supervised silhouette. |
| **use_pca** | Whether to run PCA before UMAP. PCA output used for UMAP. |
| **metric_list** | Distance metrics optimized separately with Optuna. |
| **optuna_trials** | Number of Optuna trials per metric. |
| **optuna_k_provisional** | Temporary k for silhouette scoring when no labels. |
| **selection_metric** | Criterion for choosing k (`consensus`, `silhouette`, `CH`, `DB`). |
| **random_state** | Random seed for PCA, UMAP, and KMeans. |


# Output Structure

The `fit_embedding_and_clusters(...)` function returns a dictionary with the
following fields, and also writes optional result files when `save_dir` is provided.

### Top-level outputs

| File / Key | Description |
|------------|-------------|
| **pca_df** | PCA coordinates for each sample (or `None` if PCA was disabled). |
| **pca_coordinates.csv** | Saved version of PCA coordinates (samples × PCs). |
| **summary_metrics.csv** | Summary of the best metric per distance metric (e.g., best k, silhouette, CH, DB). |

### Per-metric outputs  
Each distance metric (e.g., `"euclidean"`, `"manhattan"`, `"canberra"`, `"cosine"`) is stored under `per_metric[metric]`.

| Key / File | Description |
|------------|-------------|
| **umap_df** | Final UMAP 2D embedding (`UMAP1`, `UMAP2`). |
| **umap_coordinates.csv** | Saved UMAP coordinates for this metric. |
| **umap_params** | Best hyperparameters found by Optuna (`n_neighbors`, `min_dist`, `metric`). |
| **umap_params.json** | Saved Optuna-selected parameters. |
| **final_k** | Automatically selected number of clusters for this metric. |
| **cluster_labels** | Final KMeans cluster labels (Series aligned to `umap_df.index`). |
| **cluster_labels.csv** | Saved sample → cluster assignment. |
| **k_selection_scores.csv** | Full scoring results for all tested k (`consensus`, `silhouette`, `CH`, `DB`). |
| **k_selection_plot.png** | Plot showing the evaluation of all k values. |
| **umap_clusters.png** | UMAP colored by final clusters. |
| **umap_by_<group>.png** | UMAP colored by metadata (e.g., `disease`). |

# Adaptive Behavior

## Supervised mode (recommended)
When **`label_col`** is provided, UMAP tuning and cluster evaluation use the supplied labels
(e.g., disease, cell type) to compute **supervised silhouette scores**.  
In this mode:

- The optimizer directly evaluates embedding quality using biological labels.  
- The number of unique labels provides an **upper bound** for candidate `k`
  (capped at 50 for stability).  
- This mode generally yields **more stable**, **biologically meaningful**,  
  and **reproducible** embeddings.

> **Recommendation:**  
> Supervised mode should be used whenever biological labels (e.g., disease groups,
> cell types, conditions) are available.  
> It consistently improves cluster separation and reduces metric instability across datasets.

---

## Unsupervised mode
When **no `label_col`** is provided:

- During UMAP tuning, silhouette scores are computed using **provisional KMeans**
  with `optuna_k_provisional` clusters.  
- After UMAP optimization, the final clustering step scans a default range  
  (typically `k = 2` to ~40) to select the most appropriate number of clusters  
  using internal metrics (Silhouette, Calinski–Harabasz, Davies–Bouldin).

Unsupervised mode is fully supported, but  
results may show **higher sensitivity** to noise, metric choice, and dataset imbalance.

> **Note:**  
> Unsupervised mode is useful when no biological labels are available,  
> but supervised mode is preferred whenever such labels exist.


# Note on version locking

disint has been validated under the following tested environments:

| Component | Tested Range |
|------------|---------------|
| Python | 3.9 – 3.12 |
| NumPy | 1.26.x – 2.0.2 |
| Numba | 0.58 – 0.60 |
| umap-learn | 0.5.6 – 0.5.9.post2 |

These ranges reflect confirmed compatibility for both legacy (NumPy 1.26 / Numba 0.58)
and newer (NumPy 2.0 / Numba 0.60) configurations.
Later NumPy 2.x and Numba > 0.60 versions have not yet been validated and may
introduce upstream instability.


# Citation

If you use **disint** in your research, please cite:

1. Cong Y, Shintani M, Imanari F, Osada N, Endo T.  
   *A New Approach to Drug Repurposing with Two-Stage Prediction and Machine Learning.*  
   **OMICS**, 2022.

2. Cong Y, Osada N, Endo T.  
   *disint: A Reproducible Pipeline for Multi-Study Transcriptomic Integration and Its Application to Drug-Repositioning Analysis.*  
   **OMICS**, 2025.

# License

**disint** is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).

You are free to:
- Use, modify, and redistribute the software for non-commercial research and educational purposes.
- Share adaptations under the same license.

Under the following terms:
- **Attribution is required.**  
  You must properly cite the works listed in the *Citation* section when using this software in any research, publication, or derivative work.
- **Commercial use is prohibited** without explicit written permission.
- **Derivatives must be distributed under the same license.**

For commercial licensing, please contact: Toshinori Endo (endo@ist.hokudai.ac.jp)

© 2025 Cong Yi & Toshinori Endo. All rights reserved.
