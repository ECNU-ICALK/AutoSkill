---
id: "7161407a-1575-427e-9989-d784d2376a0c"
name: "deg-and-marker-gene-heatmap-with-viridis-col-clustering"
description: "Generates a publication-ready heatmap for differentially expressed genes (DEGs) or marker genes using viridis colormap, column-only hierarchical clustering, and Arial font — applicable to any normalized gene expression matrix with genes as rows and samples/subclusters as columns."
version: "0.1.1"
tags:
  - "bioinformatics"
  - "single-cell"
  - "scRNA-seq"
  - "heatmap"
  - "seaborn"
  - "gene-expression"
  - "marker-genes"
  - "visualization"
triggers:
  - "生成差异表达基因热图"
  - "画DEG热图"
  - "单细胞亚群标志基因热图"
  - "scRNA-seq marker gene heatmap"
  - "viridis列聚类热图"
---

# deg-and-marker-gene-heatmap-with-viridis-col-clustering

Generates a publication-ready heatmap for differentially expressed genes (DEGs) or marker genes using viridis colormap, column-only hierarchical clustering, and Arial font — applicable to any normalized gene expression matrix with genes as rows and samples/subclusters as columns.

## Prompt

# Goal
Generate a seaborn-based heatmap for differentially expressed or marker genes, accepting a pandas DataFrame with genes as rows and samples/subclusters as columns.

# Constraints & Style
- Use `cmap="viridis"` exclusively; do not use RdBu_r, center, or any other colormap or symmetry setting.
- Enable only column-wise hierarchical clustering: set `col_cluster=True` and `row_cluster=False`.
- Use Arial font for all text elements (title, axis labels, tick labels, colorbar label); enforce via `plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]` and `plt.rcParams["axes.unicode_minus"] = False`; explicitly annotate plot elements if seaborn does not inherit font settings.
- Apply row-wise z-score normalization (per gene) before plotting: `df.T.apply(lambda x: (x - x.mean()) / x.std(ddof=0)).T`.
- Use `robust=True` in `sns.heatmap` for outlier resilience.
- Set `linewidths=0.3` and `linecolor='lightgray'` for subtle cell borders.
- Set figure size to `(8, 10)`; include colorbar labeled "Z-score" with shrink=0.6.
- Title: "Differentially Expressed Genes (Z-score normalized)" or "Marker Genes (Z-score normalized)" (bold, 14pt); adapt label based on context but retain consistent phrasing.
- Axis labels: "Samples" or "Subclusters" (x), "Genes" (y); no rotation of tick labels.
- Call `plt.tight_layout()` before `plt.show()`; ensure no clipping.

# Workflow
1. Accept input DataFrame with gene-indexed rows and sample/subcluster-labeled columns.
2. Apply row-wise z-score normalization.
3. Configure matplotlib font settings for Arial compatibility.
4. Generate heatmap with specified clustering, colormap, robust scaling, layout, and labeling.
5. Display the plot.

## Triggers

- 生成差异表达基因热图
- 画DEG热图
- 单细胞亚群标志基因热图
- scRNA-seq marker gene heatmap
- viridis列聚类热图
