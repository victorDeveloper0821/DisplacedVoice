"""
Census data aggregation pipeline for the Displaced Voices project.
Fetches ACS 5-Year data for Maricopa County, AZ and merges with eviction records.
"""
import pandas as pd
import requests
from io import BytesIO
from dotenv import dotenv_values


EVICTION_URL = (
    "https://raw.githubusercontent.com/UnitForDataScience/Projects-Spring-2025"
    "/refs/heads/main/Displaced%20Voices/Data/data_geocoded.csv"
)

RACE_COLS = [
    "White Alone",
    "Black Alone",
    "Hispanic or Latino",
    "American Indian or Alaska Native Alone",
    "Asian Alone",
    "Native Hawaiian or Pacific Islander Alone",
    "Some other race",
    'Mixed race (exluding "Some other race")',
]


def load_api_key(env_path=".env"):
    return dotenv_values(env_path).get("API_KEY")


def _fetch(codes, year, state, county, api_key):
    if isinstance(codes, list):
        codes = ",".join(codes)
    url = (
        f"https://api.census.gov/data/{year}/acs/acs5"
        f"?get=NAME,{codes}&for=tract:*"
        f"&in=state:{state}&in=county:{county}&key={api_key}"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data[1:], columns=data[0])


def fetch_median_income(year, state, county, api_key):
    df = _fetch("B19013_001E", year, state, county, api_key)
    df["B19013_001E"] = df["B19013_001E"].astype(int)
    df.rename(columns={"B19013_001E": "medianIncome"}, inplace=True)
    df.drop(columns="NAME", inplace=True)
    df = df.loc[df["medianIncome"] > 0].copy()
    df["incomeLevel"] = pd.qcut(
        df["medianIncome"], q=4, labels=["Low", "Moderate", "High", "Very High"]
    )
    df["GeoID"] = df["state"] + df["county"] + df["tract"]
    return df


def fetch_occupation(year, state, county, api_key):
    codes = ["B25008_001E", "B25008_002E", "B25008_003E"]
    df = _fetch(codes, year, state, county, api_key)
    df[codes] = df[codes].astype(int)
    df["OwnerOccupied"] = df["B25008_002E"] / df["B25008_001E"]
    df["RenterOccupied"] = df["B25008_003E"] / df["B25008_001E"]
    df.drop(columns=codes + ["NAME"], inplace=True)
    df["LiveType"] = df[["OwnerOccupied", "RenterOccupied"]].idxmax(axis=1)
    df["GeoID"] = df["state"] + df["county"] + df["tract"]
    return df


def fetch_burden(year, state, county, api_key):
    codes = [f"B25070_{str(i).zfill(3)}E" for i in range(1, 11)]
    df = _fetch(codes, year, state, county, api_key)
    df[codes] = df[codes].astype(int)
    df = df.loc[df["B25070_001E"] > 0].copy()
    total = df["B25070_001E"]
    df["lowBurdan"] = (df["B25070_002E"] + df["B25070_003E"]) / total
    df["moderateBurdan"] = (df["B25070_004E"] + df["B25070_005E"]) / total
    df["costBurdan"] = (
        df[["B25070_006E", "B25070_007E", "B25070_008E", "B25070_009E"]].sum(axis=1)
    ) / total
    df["highBurdan"] = df["B25070_010E"] / total
    df.drop(columns=codes + ["NAME"], inplace=True)
    df["burden"] = df[
        ["lowBurdan", "moderateBurdan", "costBurdan", "highBurdan"]
    ].idxmax(axis=1)
    df["GeoID"] = df["state"] + df["county"] + df["tract"]
    return df


def fetch_race(year, state, county, api_key):
    codes = [
        "B02001_001E", "B02001_002E", "B02001_003E", "B03001_003E",
        "B02001_004E", "B02001_005E", "B02001_006E", "B02001_007E", "B02001_009E",
    ]
    df = _fetch(codes, year, state, county, api_key)
    for col in codes:
        df[col] = df[col].astype(float)
    total = df["B02001_001E"]
    for col in codes[1:]:
        df[col] = df[col] / total
    rename_map = {
        "B02001_001E": "Total",
        "B02001_002E": "White Alone",
        "B02001_003E": "Black Alone",
        "B03001_003E": "Hispanic or Latino",
        "B02001_004E": "American Indian or Alaska Native Alone",
        "B02001_005E": "Asian Alone",
        "B02001_006E": "Native Hawaiian or Pacific Islander Alone",
        "B02001_007E": "Some other race",
        "B02001_009E": 'Mixed race (exluding "Some other race")',
    }
    df.rename(columns=rename_map, inplace=True)
    df["Majority"] = df[RACE_COLS].idxmax(axis=1)
    df["GeoID"] = df["state"] + df["county"] + df["tract"]
    df.drop(columns=["NAME", "Total"], inplace=True)
    return df


def fetch_house_structure(year, state, county, api_key):
    codes = [
        "B25032_001E", "B25032_003E", "B25032_004E", "B25032_005E", "B25032_006E",
        "B25032_007E", "B25032_008E", "B25032_009E", "B25032_010E",
        "B25032_011E", "B25032_012E",
    ]
    df = _fetch(codes, year, state, county, api_key)
    for col in codes:
        df[col] = df[col].astype(int)
    total = df["B25032_001E"]
    result = pd.DataFrame({
        "Single-family homes": (df["B25032_003E"] + df["B25032_004E"]) / total,
        "Small multi-unit buildings (2-4 units)": (
            df["B25032_005E"] + df["B25032_006E"]
        ) / total,
        "Larger apartment complexes (5+ units)": (
            df["B25032_007E"] + df["B25032_008E"]
            + df["B25032_009E"] + df["B25032_010E"]
        ) / total,
        "Mobile homes, boats, RVs, etc.": (
            df["B25032_011E"] + df["B25032_012E"]
        ) / total,
    })
    result["majorHouseType"] = result[[
        "Single-family homes",
        "Small multi-unit buildings (2-4 units)",
        "Larger apartment complexes (5+ units)",
    ]].idxmax(axis=1)
    result[["state", "county", "tract"]] = df[["state", "county", "tract"]].values
    result = result.loc[total.values > 0].copy()
    result["GeoID"] = result["state"] + result["county"] + result["tract"]
    return result


def fetch_eviction(url=EVICTION_URL):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    df = pd.read_csv(BytesIO(r.content))
    df.dropna(subset=["geoid"], inplace=True)
    df = df[["geoid", "zip_code", "type"]].copy()
    df["zip_code"] = df["zip_code"].astype(str)
    df["GeoID"] = df["geoid"].astype(int).astype(str).str.zfill(11)
    counts = df.groupby(["GeoID", "zip_code"])["type"].count().reset_index()
    counts.rename(columns={"type": "filedEviction"}, inplace=True)
    return counts


def build_full_dataset(year="2023", state="04", county="013", env_path=".env"):
    """Fetch and merge all census tables with 2024 eviction counts."""
    api_key = load_api_key(env_path)
    drop_geo = ["state", "county", "tract"]

    df = (
        fetch_median_income(year, state, county, api_key)
        .merge(
            fetch_house_structure(year, state, county, api_key).drop(columns=drop_geo),
            how="inner", on="GeoID",
        )
        .merge(
            fetch_burden(year, state, county, api_key).drop(columns=drop_geo),
            how="inner", on="GeoID",
        )
        .merge(
            fetch_occupation(year, state, county, api_key).drop(columns=drop_geo),
            how="inner", on="GeoID",
        )
        .merge(
            fetch_race(year, state, county, api_key).drop(columns=drop_geo),
            how="inner", on="GeoID",
        )
    )
    eviction = fetch_eviction()
    df = eviction.merge(df, how="right", on="GeoID")
    df["filedEviction"] = df["filedEviction"].fillna(0).astype(int)
    df["zip_code"] = df["zip_code"].fillna("N/A")
    return df
