# Displaced Voices: Eviction Patterns in Maricopa County, AZ

An analysis of 2024 eviction filings across Maricopa County census tracts, integrating U.S. Census ACS 5-year demographic data to identify the socioeconomic drivers of housing displacement.

---

## District-Based Segmentation

K-means clustering partitions 1,533 Maricopa County census tracts into two distinct groups based on income, racial/ethnic composition, housing structure, and rent burden:

| | Cluster 1 (High Displacement) | Cluster 2 (Low Displacement) |
|---|---|---|
| Tracts | 1,046 | 487 |
| Mean evictions per tract | 44.6 | 12.9 |
| Typical income | Lower (< $100K median) | Higher |
| Dominant ethnicity | Mixed / Hispanic | Predominantly White |
| Rent burden profile | Higher share of cost- and severely burdened households | Lower burden concentration |

Cluster membership is retained as a fixed effect in all regression models to control for neighborhood-level differences not captured by individual predictors.

---

## Key Findings

- **Cluster 2 tracts have 24% fewer evictions than Cluster 1** (IRR = 0.760). After controlling for income, tenure, burden, and race, tracts with higher median household income and predominantly White populations exhibit meaningfully lower eviction rates. This suggests that neighborhood-level socioeconomic advantage operates independently of individual predictors.

- **Median income provides a modest but consistent protective effect** (IRR = 0.963 per $10,000 increase, −3.7%). While income growth reduces eviction risk, the effect is not large enough to offset housing cost pressures on its own.

- **Shifting households from low to severe rent burden increases eviction rates by 6.3% per 10 percentage-point shift.** Because burden proportions sum to approximately 1, the key driver is not any single tier in isolation but the movement of households out of lower-burden categories into cost-burdened (30–49%) or severely burdened (50%+) tiers. This makes rent affordability the primary structural lever for reducing eviction risk.

---

## Solution Overview

- **District-Based Segmentation** — K-means partitions 1,533 census tracts into two groups: a high-displacement cluster (1,046 tracts; mean = 44.6 evictions per tract) and a low-displacement cluster (487 tracts; mean = 12.9). These groups differ substantially in median income, racial/ethnic composition, and rent burden distribution.

- **Modeling Approach** — The analysis initially used a linear mixed-effects model (`mixedlm`) with cluster as a random effect. Because eviction counts are discrete non-negative integers, the approach shifted to count regression: Poisson first, followed by a negative binomial model after detecting overdispersion (variance >> mean across clusters). Cluster is included as a fixed effect in the final model.

---

## Tech Stack

- **Visualization** — `matplotlib`, `seaborn`, `plotly`  
- **Data Processing** — `pandas`, `numpy`, `geopandas`, `python-dotenv`, Census ACS API, `scikit-learn` (KMeans, StandardScaler)  
- **Statistical Modeling** — `statsmodels` (mixedlm, VIF), `scikit-learn` (silhouette score)