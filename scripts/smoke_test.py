from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

EXPECTED_OUTPUTS = [
    "data_quality_summary.csv",
    "vif_table.csv",
    "jarque_bera.csv",
    "residual_correlation_matrix.csv",
    "breusch_pagan_residual_correlation.csv",
    "sur_estimation_sample_summary.csv",
    "sur_country_results.csv",
    "female_employment_coefficients.csv",
    "comparison_with_original_table6.csv",
    "ols_vs_sur_female_employment.csv",
    "balanced_vs_available_ols.csv",
]

EXPECTED_FIGURES = [
    "gdp_trends_by_country.png",
    "female_employment_trends_by_country.png",
    "female_employment_vs_gdp.png",
    "correlation_matrix.png",
]


def run(script):
    subprocess.run([PYTHON, str(ROOT / script)], check=True)


def main():
    run("src/sync_processed_data.py")
    run("src/run_analysis.py")
    run("scripts/create_visuals.py")

    output_dir = ROOT / "output" / "tables"
    missing = [name for name in EXPECTED_OUTPUTS if not (output_dir / name).exists()]

    figures_dir = ROOT / "output" / "figures"
    missing_figures = [name for name in EXPECTED_FIGURES if not (figures_dir / name).exists()]

    if missing:
        raise FileNotFoundError(f"Smoke test failed. Missing outputs: {missing}")
    if missing_figures:
        raise FileNotFoundError(f"Smoke test failed. Missing figures: {missing_figures}")

    print("Smoke test passed.")
    print(f"Verified outputs in: {output_dir}")
    print(f"Verified figures in: {figures_dir}")


if __name__ == "__main__":
    main()
