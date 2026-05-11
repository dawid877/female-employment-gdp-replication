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
    Keep only years available for all six countries after complete-case filtering.

    In the current cleaned dataset, this gives 1995-2022 because Poland starts in 1995.
    This is required for SUR in linearmodels, because all equations must have aligned
    observations.
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


def build_sur_equations(df):
    """
    Build one SUR equation per country.
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


def extract_lerf_from_sur(results, sample_name):
    """
    Extract only the female-employment coefficient from SUR results.
    """
    rows = []

    for param_name in results.params.index:
        country, variable = param_name.split("_", 1)

        if variable == "lerf":
            rows.append({
                "sample": sample_name,
                "model": "SUR",
                "country": country,
                "coefficient": results.params[param_name],
                "std_error": results.std_errors[param_name],
                "t_stat": results.tstats[param_name],
                "p_value": results.pvalues[param_name],
                "significant_5pct": results.pvalues[param_name] < 0.05,
            })

    return pd.DataFrame(rows)


def run_sur(df, sample_name):
    """
    Estimate SUR and return female-employment results.
    """
    equations = build_sur_equations(df)
    model = SUR(equations)
    results = model.fit(cov_type="robust")

    return extract_lerf_from_sur(results, sample_name)


def run_country_ols(df, sample_name):
    """
    Estimate separate OLS models by country.

    Unlike SUR, OLS can be estimated on different sample lengths by country.
    """
    rows = []

    for code, name in COUNTRY_NAMES.items():
        country_df = df[df["country_code"] == code].copy()

        model_df = country_df[
            ["year", "lgdp", "ltrd", "lup", "lerf", "lfce"]
        ].dropna()

        if model_df.empty:
            raise ValueError(f"No usable observations for {name} ({code}).")

        y = model_df["lgdp"]
        x = sm.add_constant(model_df[["ltrd", "lup", "lerf", "lfce"]])

        model = sm.OLS(y, x).fit(cov_type="HC1")

        rows.append({
            "sample": sample_name,
            "model": "OLS",
            "country": name,
            "start_year": int(model_df["year"].min()),
            "end_year": int(model_df["year"].max()),
            "observations": int(model_df.shape[0]),
            "coefficient": model.params["lerf"],
            "std_error": model.bse["lerf"],
            "t_stat": model.tvalues["lerf"],
            "p_value": model.pvalues["lerf"],
            "significant_5pct": model.pvalues["lerf"] < 0.05,})

    return pd.DataFrame(rows)


def ols_vs_sur_comparison(df):
    """
    Compare female-employment coefficients from separate OLS and SUR
    on the same balanced 1995-2022 sample.

    This checks whether the SUR framework changes conclusions relative
    to estimating each country equation separately.
    """
    balanced = make_balanced_sample(df)

    ols_results = run_country_ols(balanced, sample_name="balanced_1995_2022")
    sur_results = run_sur(balanced, sample_name="balanced_1995_2022")

    comparison = ols_results.merge(
        sur_results,
        on="country",
        suffixes=("_ols", "_sur"),)

    comparison = comparison[[
        "country",
        "coefficient_ols",
        "std_error_ols",
        "p_value_ols",
        "significant_5pct_ols",
        "coefficient_sur",
        "std_error_sur",
        "p_value_sur",
        "significant_5pct_sur",]]

    comparison["coefficient_difference_sur_minus_ols"] = (
        comparison["coefficient_sur"] - comparison["coefficient_ols"])

    comparison["same_significance_conclusion"] = (
        comparison["significant_5pct_ols"]
        == comparison["significant_5pct_sur"])

    return comparison


def balanced_vs_available_ols(df):
    """
    Compare separate OLS estimates using:

    1. The balanced common sample, 1995-2022.
    2. Each country's maximum available complete-case sample.

    This replaces the unavailable 'maximum available SUR' check, because
    linearmodels SUR requires all equations to have the same number of observations.
    """
    balanced = make_balanced_sample(df)
    complete = df.dropna(subset=["lgdp", "ltrd", "lup", "lerf", "lfce"]).copy()

    balanced_ols = run_country_ols(
        balanced,
        sample_name="balanced_1995_2022",)

    available_ols = run_country_ols(
        complete,
        sample_name="maximum_available_by_country",)

    comparison = balanced_ols.merge(
        available_ols,
        on="country",
        suffixes=("_balanced", "_available"),)

    comparison = comparison[[
        "country",
        "start_year_balanced",
        "end_year_balanced",
        "observations_balanced",
        "coefficient_balanced",
        "std_error_balanced",
        "p_value_balanced",
        "significant_5pct_balanced",
        "start_year_available",
        "end_year_available",
        "observations_available",
        "coefficient_available",
        "std_error_available",
        "p_value_available",
        "significant_5pct_available",]]

    comparison["coefficient_difference_available_minus_balanced"] = (
        comparison["coefficient_available"]
        - comparison["coefficient_balanced"])

    comparison["same_significance_conclusion"] = (
        comparison["significant_5pct_balanced"]
        == comparison["significant_5pct_available"])

    return comparison


def main():
    df = load_data()

    ols_sur = ols_vs_sur_comparison(df)
    balanced_available_ols = balanced_vs_available_ols(df)

    ols_sur.to_csv(
        OUT_TABLES / "ols_vs_sur_female_employment.csv",
        index=False,)

    balanced_available_ols.to_csv(
        OUT_TABLES / "balanced_vs_available_ols.csv",
        index=False,)

    print("Robustness checks completed.")
    print(f"Saved tables to: {OUT_TABLES}")
    print(
        "Note: maximum-available SUR was not estimated because SUR requires "
        "aligned observations across equations. The sample-sensitivity check "
        "is therefore implemented using separate country OLS models.")


if __name__ == "__main__":
    main()