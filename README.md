# Displaced Voices: Eviction Patterns in Maricopa County, AZ

Analysis of 2024 eviction filings across Maricopa County census tracts, integrating U.S. Census ACS 5-Year demographic data to identify socioeconomic drivers of housing displacement.

---

## Project Structure

```
DisplacedVoice/
├── DataStory.ipynb          # Main analysis notebook (data story)
├── census_data.py           # Census API data pipeline (fetching & merging)
├── requirements.txt         # Python dependencies
└── .env                     # Census API key (not committed)
```

> `ClusteringAnalysis.ipynb` and `RegressionAnalysis.ipynb` are legacy notebooks superseded by `DataStory.ipynb`.

---

## Setup

**1. Create and activate the virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install jupyterlab ipykernel
python -m ipykernel install --user --name displacedvoice --display-name "DisplacedVoice"
```

**2. Add your Census API key:**
```bash
echo "API_KEY=your_key_here" > .env
```
Get a free key at [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html).

**3. Launch Jupyter:**
```bash
jupyter lab
```
Open `DataStory.ipynb` and select the **DisplacedVoice** kernel.

---

## Analysis Flow

### 1. Descriptive Statistics
Overview of all Maricopa County census tracts:
- **Median income** — histogram and boxplot by income quartile (Low / Moderate / High / Very High)
- **Racial/ethnic majority** — pie chart of tract-level majority race
- **Gross rent burden** — pie chart of dominant burden level per tract (Low / Moderate / Cost-Burdened / Severely Burdened)
- **Housing unit structure** — pie chart of dominant housing type per tract

### 2. K-Means Clustering
Census tracts are clustered using K-means on continuous demographic and housing features. `medianIncome` is standardized with `StandardScaler`; all other features are proportions on [0, 1].

Optimal `k` is selected using four metrics:

| Metric | Goal |
|---|---|
| Elbow (WCSS) | Identify diminishing returns |
| Silhouette Score | Higher = more compact clusters |
| Calinski-Harabasz Index | Higher = better separation |
| Davies-Bouldin Index | Lower = better separation |

**Selected k = 9** based on the elbow inflection and plateau across all four metrics.

### 3. Cluster Profiles
Per-cluster visualizations to characterize each group:
- Median income and filed eviction boxplots
- Stacked racial/ethnic composition bar chart
- Grouped rent burden composition bar chart

### 4. Collinearity Analysis
Compositional variable groups (proportions summing to ~1) produce collinearity. Identified groups and resolutions:

| Group | Variables | Resolution |
|---|---|---|
| Tenure | `OwnerOccupied` + `RenterOccupied` = 1 | Keep `RenterOccupied` only |
| Rent Burden | 4 burden proportions ≈ 1 | Drop `highBurdan` as reference |
| Housing Structure | 4 housing type proportions ≈ 1 | Drop `mobile_other` as reference |

Visualized via **pairplots** (burden and housing groups) and a **correlation heatmap + VIF table** for the reduced variable set.

### 5. Linear Mixed-Effects Models
Since census tract clusters are a categorical grouping variable, `mixedlm` is used with **cluster as the random effect**. Dependent variable: `log(filedEviction + 1)`.

Five models are fit, one per variable group:

| Model | Fixed Effects |
|---|---|
| Income | `medianIncome`, `C(incomeLevel)` |
| Live Type | `RenterOccupied`, `C(LiveType)` |
| Burden | `lowBurdan`, `moderateBurdan`, `costBurdan`, `C(burden)` |
| Race | `white`, `black`, `latino`, `native_american`, `asian`, `C(Majority)` |
| House Type | `single_family`, `small_multi`, `large_apartment`, `C(majorHouseType)` |

### 6. Final Model & Interpretation
Significant predictors are selected using **two simultaneous criteria**:
1. **p-value < 0.05**
2. **95% CI excludes zero** (both bounds share the same sign)

A final `mixedlm` is fit on the retained predictors.

**Key findings:**
- **Rent burden is the strongest predictor** — tracts where residents spend 20–49% of income on rent show substantially higher eviction rates
- **Median income mediates but does not eliminate risk** — income alone does not protect against eviction once burden is controlled
- **Racial composition is not independently significant** — racial disparities are largely mediated by income, tenure, and burden
- **Cluster-level random effects are significant** — neighborhood context beyond individual tract characteristics matters for eviction outcomes

---

## Data Sources

| Dataset | Source | Year |
|---|---|---|
| Median Household Income (B19013) | U.S. Census ACS 5-Year | 2023 |
| Housing Tenure (B25008) | U.S. Census ACS 5-Year | 2023 |
| Gross Rent as % of Income (B25070) | U.S. Census ACS 5-Year | 2023 |
| Race & Ethnicity (B02001, B03001) | U.S. Census ACS 5-Year | 2023 |
| Housing Unit Structure (B25032) | U.S. Census ACS 5-Year | 2023 |
| Eviction Filings | Maricopa County Court Records (geocoded) | 2024 |

---

## Dependencies

| Package | Purpose |
|---|---|
| `pandas`, `numpy` | Data manipulation |
| `geopandas` | Spatial data support |
| `matplotlib`, `seaborn` | Visualization |
| `scikit-learn` | K-means clustering, scaling, metrics |
| `statsmodels` | Linear mixed-effects models, VIF |
| `plotly` | Interactive charts |
| `python-dotenv` | API key management |
