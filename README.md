# Displaced Voices: Eviction Patterns in Maricopa County, AZ

Analysis of 2024 eviction filings across Maricopa County census tracts, integrating U.S. Census ACS 5-Year demographic data to identify socioeconomic drivers of housing displacement.

---

## District-Based Segmentation

K-Means clustering partitioned 1,533 Maricopa County census tracts into two distinct groups based on income, racial/ethnic composition, housing structure, and rent burden:

| | Cluster 1 (High-Displacement) | Cluster 2 (Low-Displacement) |
|---|---|---|
| Tracts | 1,046 | 487 |
| Mean evictions / tract | 44.6 | 12.9 |
| Typical income | Lower (< $100k median) | Higher |
| Dominant ethnicity | Mixed / Hispanic | Predominantly White |
| Rent burden profile | Higher share of cost- and severely-burdened households | Lower burden concentration |

Cluster membership is retained as a fixed effect in all regression models to control for neighborhood-level differences not captured by individual predictors.

---

## Key Findings

- **Cluster 2 tracts file 24% fewer evictions than Cluster 1** (IRR = 0.760) — after controlling for income, tenure, burden, and race, tracts with higher median household income and predominantly White composition have a meaningfully lower eviction rate, confirming that neighborhood-level socioeconomic advantage operates independently of individual predictors
- **Median income provides a modest but reliable protective effect** (IRR = 0.963 per $10,000 increase, −3.7%) — income growth reduces eviction risk, but the effect is too small to offset housing cost pressure on its own
- **Shifting households from low burden to severe burden raises the eviction rate by 6.3% per 10 percentage points** — because burden proportions sum to ~1, the key driver is not any single tier in isolation but the escalation of households out of lower burden categories into cost-burdened (30–49%) or severely-burdened (50%+) tiers, making rent affordability the primary structural lever for reducing eviction risk

---

## Solution Overview

- **District-Based Segmentation** — K-Means partitioned 1,533 Maricopa County census tracts into two distinct groups: a high-displacement cluster (1,046 tracts, mean 44.6 evictions/tract) and a low-displacement cluster (487 tracts, mean 12.9 evictions/tract). The two groups differ markedly in median income, racial/ethnic composition, and rent burden distribution
- **Modeling** — Initially used Linear Mixed-Effects (`mixedlm`) with cluster as random effect. Since eviction counts are discrete non-negative integers, switched to count regression — Poisson first, then Negative Binomial after detecting overdispersion (variance >> mean across clusters). Cluster is included as a fixed effect in the final count model

---

## Tech Stack

- **Visualization** — `matplotlib`, `seaborn`, `plotly`
- **Data Operations** — `pandas`, `numpy`, `geopandas`, `python-dotenv`, Census ACS API, `scikit-learn` (KMeans, StandardScaler)
- **Statistical Modeling** — `statsmodels` (mixedlm, VIF), `scikit-learn` (silhouette score)

