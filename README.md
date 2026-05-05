# Displaced Voices: Eviction Patterns in Maricopa County, AZ

Analysis of 2024 eviction filings across Maricopa County census tracts, integrating U.S. Census ACS 5-Year demographic data to identify socioeconomic drivers of housing displacement.

---

## Key Findings

- **Rent burden is the strongest predictor of eviction** — tracts where residents spend 20–49% of income on rent show substantially higher eviction rates, even after controlling for income
- **Median income mediates but does not eliminate risk** — income alone does not protect against eviction once rent burden is accounted for
- **Racial composition is not independently significant** — racial disparities are largely mediated by income, tenure, and burden rather than race itself
- **Neighborhood context matters** — cluster-level random effects are statistically significant, confirming that tract-level demographics do not fully explain eviction risk; local housing market dynamics play an independent role

---

## Solution Overview

- **District-Based Segmentation** — K-Means partitioned 1,533 Maricopa County census tracts into two distinct groups: a high-displacement cluster (1,046 tracts, mean 44.6 evictions/tract) and a low-displacement cluster (487 tracts, mean 12.9 evictions/tract). The two groups differ markedly in median income, racial/ethnic composition, and rent burden distribution
- **Modeling** — Initially used Linear Mixed-Effects (`mixedlm`) with cluster as random effect. Since eviction counts are discrete non-negative integers, switched to count regression — Poisson first, then Negative Binomial after detecting overdispersion (variance >> mean across clusters). Cluster is included as a fixed effect in the final count model

---

## Tech Stack

- **Visualization** — `matplotlib`, `seaborn`, `plotly`
- **Data Operations** — `pandas`, `numpy`, `geopandas`, `python-dotenv`, Census ACS API, `scikit-learn` (KMeans, StandardScaler)
- **Statistical Modeling** — `statsmodels` (mixedlm, VIF), `scikit-learn` (silhouette score)

