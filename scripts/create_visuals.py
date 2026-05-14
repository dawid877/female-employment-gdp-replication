from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "panel_data.csv"
FIGURES_DIR = ROOT / "output" / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def get_col(df, names):
    for name in names:
        if name in df.columns:
            return name
    raise ValueError(f"Could not find any of these columns: {names}")


def main():
    df = pd.read_csv(DATA_PATH)

    print("Columns in dataset:")
    print(df.columns.tolist())

    country_col = get_col(df, ["country", "Country", "country_name"])
    year_col = get_col(df, ["year", "Year"])

    gdp_col = get_col(df, ["lgdp", "gdp", "GDP"])
    female_emp_col = get_col(df, ["lerf", "erf", "female_employment"])

    trade_col = get_col(df, ["ltrd", "trd", "trade"])
    urban_col = get_col(df, ["lup", "up", "urban_population"])
    consumption_col = get_col(df, ["lfce", "fce", "final_consumption"])

    # 1. GDP trends
    plt.figure(figsize=(10, 6))
    for country, group in df.groupby(country_col):
        group = group.sort_values(year_col)
        plt.plot(group[year_col], group[gdp_col], marker="o", linewidth=1.5, label=country)

    plt.title("GDP Trends in CEE Countries")
    plt.xlabel("Year")
    plt.ylabel("Log GDP")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "gdp_trends_by_country.png", dpi=300)
    plt.close()

    # 2. Female employment trends
    plt.figure(figsize=(10, 6))
    for country, group in df.groupby(country_col):
        group = group.sort_values(year_col)
        plt.plot(group[year_col], group[female_emp_col], marker="o", linewidth=1.5, label=country)

    plt.title("Female Employment Trends in CEE Countries")
    plt.xlabel("Year")
    plt.ylabel("Log female employment")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "female_employment_trends_by_country.png", dpi=300)
    plt.close()

    # 3. Female employment vs GDP
    plt.figure(figsize=(8, 6))
    for country, group in df.groupby(country_col):
        plt.scatter(group[female_emp_col], group[gdp_col], label=country, alpha=0.75)

    plt.title("Female Employment and GDP")
    plt.xlabel("Log female employment")
    plt.ylabel("Log GDP")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "female_employment_vs_gdp.png", dpi=300)
    plt.close()

    # 4. Correlation matrix
    variables = [gdp_col, female_emp_col, trade_col, urban_col, consumption_col]
    corr = df[variables].corr()

    plt.figure(figsize=(8, 6))
    plt.imshow(corr)
    plt.colorbar(label="Correlation")

    plt.xticks(range(len(variables)), variables, rotation=45, ha="right")
    plt.yticks(range(len(variables)), variables)

    for i in range(len(variables)):
        for j in range(len(variables)):
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")

    plt.title("Correlation Matrix of Model Variables")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "correlation_matrix.png", dpi=300)
    plt.close()

    print("Visuals created successfully.")
    print(f"Saved in: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
