from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy.stats import jarque_bera, chi2


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "panel_data.csv"
OUT_TABLES = ROOT / "output" / "tables"
OUT_TABLES.mkdir(parents=True, exist_ok=True)


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


def data_quality_summary(df):
    """
    Summarise time coverage and missing values by country.
    This helps document the unbalanced part of the dataset.
    """
    return (
        df.groupby(["country_code", "country"])
        .agg(
            start_year=("year", "min"),
            end_year=("year", "max"),
            observations=("year", "count"),
            missing_lgdp=("lgdp", lambda x: x.isna().sum()),
            missing_lerf=("lerf", lambda x: x.isna().sum()),
            missing_lup=("lup", lambda x: x.isna().sum()),
            missing_ltrd=("ltrd", lambda x: x.isna().sum()),
            missing_lfce=("lfce", lambda x: x.isna().sum()),)
        .reset_index())


def calculate_vif(df):
    """
    Calculate VIF values for the explanatory variables.
    VIF checks multicollinearity.
    """
    predictors = ["ltrd", "lup", "lerf", "lfce"]

    model_df = df[predictors].dropna()
    x = sm.add_constant(model_df)

    rows = []

    for i, col in enumerate(x.columns):
        if col == "const":
            continue

        vif_value = variance_inflation_factor(x.values, i)

        rows.append({
            "variable": col,
            "vif": vif_value,
            "rule_of_thumb": "acceptable_below_5",
            "interpretation": (
                "acceptable" if vif_value < 5 else "potential_multicollinearity"),
        })

    return pd.DataFrame(rows)


def jarque_bera_test(df):
    """
    Run a Jarque-Bera test on residuals from a pooled OLS model.
    This is used as a residual normality diagnostic.
    """
    model_df = df[["lgdp", "ltrd", "lup", "lerf", "lfce"]].dropna()

    y = model_df["lgdp"]
    x = sm.add_constant(model_df[["ltrd", "lup", "lerf", "lfce"]])

    model = sm.OLS(y, x).fit()
    stat, pvalue = jarque_bera(model.resid)

    return pd.DataFrame([{
        "test": "Jarque-Bera",
        "statistic": stat,
        "p_value": pvalue,
        "interpretation": (
            "do_not_reject_normality" if pvalue >= 0.05 else "reject_normality"),
    }])


def get_country_residuals(df):
    """
    Estimate separate OLS equations by country and collect residuals.
    Residual correlations are used to evaluate whether SUR is appropriate.
    """
    residuals = []

    for country_code, group in df.groupby("country_code"):
        model_df = group[["year", "lgdp", "ltrd", "lup", "lerf", "lfce"]].dropna()

        y = model_df["lgdp"]
        x = sm.add_constant(model_df[["ltrd", "lup", "lerf", "lfce"]])

        model = sm.OLS(y, x).fit()

        residuals.append(pd.DataFrame({
            "year": model_df["year"].values,
            "country_code": country_code,
            "residual": model.resid.values,}))

    residuals = pd.concat(residuals, ignore_index=True)

    return (
        residuals
        .pivot(index="year", columns="country_code", values="residual")
        .dropna())


def breusch_pagan_residual_correlation(residuals):
    """
    Breusch-Pagan LM test for cross-equation residual correlation.

    Null hypothesis:
    residuals across country equations are independent.

    Alternative hypothesis:
    residuals across country equations are correlated.
    """
    corr = residuals.corr()

    n = corr.shape[0]
    t = residuals.shape[0]

    lm_stat = 0

    for i in range(n):
        for j in range(i + 1, n):
            lm_stat += corr.iloc[i, j] ** 2

    lm_stat = t * lm_stat
    degrees_freedom = n * (n - 1) / 2
    p_value = 1 - chi2.cdf(lm_stat, degrees_freedom)

    return pd.DataFrame([{
        "test": "Breusch-Pagan residual correlation",
        "lm_statistic": lm_stat,
        "df": degrees_freedom,
        "p_value": p_value,
        "interpretation": (
            "evidence_of_cross_equation_correlation"
            if p_value < 0.05
            else "weak_evidence_of_cross_equation_correlation"),}])


def main():
    df = load_data()

    quality = data_quality_summary(df)
    vif_table = calculate_vif(df)
    jb_table = jarque_bera_test(df)

    residuals = get_country_residuals(df)
    residual_corr = residuals.corr()
    bp_table = breusch_pagan_residual_correlation(residuals)

    quality.to_csv(OUT_TABLES / "data_quality_summary.csv", index=False)
    vif_table.to_csv(OUT_TABLES / "vif_table.csv", index=False)
    jb_table.to_csv(OUT_TABLES / "jarque_bera.csv", index=False)
    residual_corr.to_csv(OUT_TABLES / "residual_correlation_matrix.csv")
    bp_table.to_csv(OUT_TABLES / "breusch_pagan_residual_correlation.csv", index=False)

    print("Diagnostics completed.")
    print(f"Saved tables to: {OUT_TABLES}")


if __name__ == "__main__":
    main()