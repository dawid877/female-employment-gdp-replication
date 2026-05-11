from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_TABLES = ROOT / "output" / "tables"


def main():
    updated_path = OUT_TABLES / "female_employment_coefficients.csv"

    if not updated_path.exists():
        raise FileNotFoundError(
            "female_employment_coefficients.csv not found. "
            "Run src/sur_model.py first.")

    updated = pd.read_csv(updated_path)

    original = pd.DataFrame({
        "country": [
            "Hungary",
            "Czechia",
            "Poland",
            "Romania",
            "Bulgaria",
            "Greece",],
        "paper_lerf_coefficient": [
            0.139,
            0.505,
            0.130,
            -0.060,
            0.231,
            0.020,],
        "paper_significant_5pct": [
            True,
            True,
            False,
            False,
            True,
            False,],
    })

    comparison = original.merge(
        updated[[
            "country",
            "coefficient",
            "std_error",
            "t_stat",
            "p_value",
            "significant_5pct",]],
        on="country",
        how="left",
    )

    comparison = comparison.rename(columns={
        "coefficient": "updated_lerf_coefficient",
        "std_error": "updated_std_error",
        "t_stat": "updated_t_stat",
        "p_value": "updated_p_value",
        "significant_5pct": "updated_significant_5pct",})

    comparison["coefficient_difference"] = (
        comparison["updated_lerf_coefficient"]
        - comparison["paper_lerf_coefficient"])

    comparison["same_significance_conclusion"] = (
        comparison["paper_significant_5pct"]
        == comparison["updated_significant_5pct"] )

    comparison.to_csv(
        OUT_TABLES / "comparison_with_original_table6.csv",
        index=False,)

    print("Comparison with original paper completed.")
    print(f"Saved table to: {OUT_TABLES / 'comparison_with_original_table6.csv'}")


if __name__ == "__main__":
    main()