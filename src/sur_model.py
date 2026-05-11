from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from linearmodels.system import SUR


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "panel_data.csv"
OUT_TABLES = ROOT / "output" / "tables"
OUT_TABLES.mkdir(parents=True, exist_ok=True)


COUNTRY_NAMES = {
    "HUN": "Hungary",
    "CZE": "Czechia",
    "POL": "Poland",
    "ROU": "Romania",
    "BGR": "Bulgaria",
    "GRC": "Greece",}


REQUIRED_COLUMNS = [
    "country_code",
    "country",
    "year",
    "lgdp",
    "lerf",
    "lup",
    "ltrd",
    "lfce",]


def load_data():
    """
    Load and validate the cleaned logged World Bank dataset.
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {DATA_PATH}. "
            "Save the cleaned World Bank data as data/processed/panel_data.csv.")

    df = pd.read_csv(DATA_PATH)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df = df.copy()
    df["year"] = df["year"].astype(int)

    for col in ["lgdp", "lerf", "lup", "ltrd", "lfce"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def make_balanced_sample(df):
    """
    Keep only years available for all six countries after dropping missing values.

    This is important because the cleaned data is slightly unbalanced:
    Poland has missing early observations after complete-case filtering.
    A balanced SUR sample keeps the country equations comparable.
    """
    required_codes = set(COUNTRY_NAMES.keys())

    complete = df.dropna(subset=["lgdp", "ltrd", "lup", "lerf", "lfce"])

    available_by_year = complete.groupby("year")["country_code"].apply(set)

    common_years = [
        year for year, codes in available_by_year.items()
        if required_codes.issubset(codes)]

    if not common_years:
        raise ValueError("No common years available across all six countries.")

    balanced = complete[complete["year"].isin(common_years)].copy()
    balanced = balanced.sort_values(["country_code", "year"]).reset_index(drop=True)

    return balanced


def sample_summary(df):
    """
    Summarise the actual estimation sample used by the SUR model.
    """
    return (
        df.groupby(["country_code", "country"])
        .agg(
            start_year=("year", "min"),
            end_year=("year", "max"),
            observations=("year", "count"),)
        .reset_index())


def build_equations(df):
    """
    Build one GDP equation for each country.

    Model:
    lgdp = const + ltrd + lup + lerf + lfce + error
    """
    equations = {}

    for code, name in COUNTRY_NAMES.items():
        country_df = df[df["country_code"] == code].copy()

        country_df = country_df[
            ["lgdp", "ltrd", "lup", "lerf", "lfce"]
        ].dropna()

        if country_df.empty:
            raise ValueError(f"No usable observations for {name} ({code}).")

        y = country_df["lgdp"]
        x = sm.add_constant(country_df[["ltrd", "lup", "lerf", "lfce"]])

        equations[name] = {
            "dependent": y,
            "exog": x,}

    return equations


def extract_results(results):
    """
    Convert linearmodels SUR output into a clean table.
    """
    rows = []

    for param_name in results.params.index:
        country, variable = param_name.split("_", 1)

        rows.append({
            "country": country,
            "variable": variable,
            "coefficient": results.params[param_name],
            "std_error": results.std_errors[param_name],
            "t_stat": results.tstats[param_name],
            "p_value": results.pvalues[param_name],
            "significant_5pct": results.pvalues[param_name] < 0.05,})

    return pd.DataFrame(rows)


def main():
    df = load_data()

    estimation_df = make_balanced_sample(df)

    summary_table = sample_summary(estimation_df)
    summary_table.to_csv(
        OUT_TABLES / "sur_estimation_sample_summary.csv",
        index=False,)

    equations = build_equations(estimation_df)

    model = SUR(equations)
    results = model.fit(cov_type="robust")

    print(results.summary)

    results_table = extract_results(results)

    results_table.to_csv(
        OUT_TABLES / "sur_country_results.csv",
        index=False,)

    female_employment_results = results_table[
        results_table["variable"] == "lerf"
    ].copy()

    female_employment_results.to_csv(
        OUT_TABLES / "female_employment_coefficients.csv",
        index=False,)

    print("SUR model completed.")
    print(f"Saved tables to: {OUT_TABLES}")


if __name__ == "__main__":
    main()