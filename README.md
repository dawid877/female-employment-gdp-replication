# Evaluation of the Impact of Women's Employment on GDP in CEE Countries

## Authors

- Dawid Grzesiak 473172
- Kostiantyn Okhrimenko 473494
- Zarina Khalilova 476692
- Nyasha Nyarirangwe 474895

## What this repository reproduces

This repository reproduces the Python implementation of the Seemingly Unrelated Regression (SUR) analysis used for the project based on `Women's unemployment.pdf` by Asli Okay Toprak (2025). The study examines Hungary, Czechia, Poland, Romania, Bulgaria, and Greece over the 1992-2022 period, using GDP as the dependent variable and female employment, urban population, trade, and final consumption expenditure as explanatory variables.

The current presentation-day run reproduces the modeling stage from the committed processed dataset in `data/processed/panel_data.csv`. A separate notebook-based workflow for collecting raw World Bank data is also included in the repository.

## Paper and replication scope

- Target paper: `Women's unemployment.pdf`
- Econometric approach: SUR with country-specific equations
- Main modeling entrypoint: `src/run_analysis.py`
- Data handoff helper: `src/sync_processed_data.py`
- Validation helper: `scripts/smoke_test.py`
- Notes on paper-vs-repo differences: `REPLICATION_NOTES.md`
- Preserved original proposal README: `Project_Proposal_Readme.md`

## Data sources

The repository uses World Bank indicators corresponding to the study:

- GDP (constant 2015 US$): [NY.GDP.MKTP.KD](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD)
- Employment to population ratio, 15+, female (%), modeled ILO estimate: [SL.EMP.TOTL.SP.FE.ZS](https://data.worldbank.org/indicator/SL.EMP.TOTL.SP.FE.ZS)
- Urban population (% of total population): [SP.URB.TOTL.IN.ZS](https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS)
- Trade (% of GDP): [NE.TRD.GNFS.ZS](https://data.worldbank.org/indicator/NE.TRD.GNFS.ZS)
- Final consumption expenditure (constant 2015 US$): [NE.CON.TOTL.KD](https://data.worldbank.org/indicator/NE.CON.TOTL.KD)

## Requirements

- Python 3.13 was used for the validated run in this repository
- Windows PowerShell commands are shown below
- `virtualenv` is recommended for the isolated presentation-day environment
- No external credentials are required for the current demo run because the processed dataset is already committed

## Quick demo run

From a freshly cloned repository, run:

```powershell
git clone https://github.com/dawid877/female-employment-gdp-replication.git
cd female-employment-gdp-replication
python -m pip install --user virtualenv
python -m virtualenv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python src\sync_processed_data.py
.\.venv\Scripts\python src\run_analysis.py
```

This sequence will:

1. Clone the repository into a fresh folder
2. Create an isolated Python environment with `virtualenv`
3. Install the pinned Python dependencies
4. Sync the committed logged dataset into the modeling input path
5. Run the diagnostics, SUR model, paper comparison, and robustness scripts

## Manual step-by-step run

If you prefer to run the commands yourself:

```powershell
git clone https://github.com/dawid877/female-employment-gdp-replication.git
cd female-employment-gdp-replication
python -m pip install --user virtualenv
python -m virtualenv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python src\sync_processed_data.py
.\.venv\Scripts\python src\run_analysis.py
```

This is the recommended presentation-day flow because it uses an isolated environment without depending on the built-in `venv` bootstrap.

## Optional raw-data refresh

The repository also contains a separate notebook for collecting raw World Bank data:

- `data/collection_preprocessing.ipynb`

That notebook writes logged data to `data/data/wdi_wide_logged.csv`. To align that notebook output with the modeling input expected by the analysis scripts, run:

```powershell
.\.venv\Scripts\python src\sync_processed_data.py
```

This keeps the modeling input `data/processed/panel_data.csv` synchronized without changing the original analysis scripts.

## Expected outputs

After a successful run, the main generated outputs are CSV tables in `output/tables/`:

- `data_quality_summary.csv`
- `vif_table.csv`
- `jarque_bera.csv`
- `residual_correlation_matrix.csv`
- `breusch_pagan_residual_correlation.csv`
- `sur_estimation_sample_summary.csv`
- `sur_country_results.csv`
- `female_employment_coefficients.csv`
- `comparison_with_original_table6.csv`
- `ols_vs_sur_female_employment.csv`
- `balanced_vs_available_ols.csv`

The repository also includes already committed figures in `data/visuals/`.

## Expected runtime

- First run with environment setup: usually a few minutes, depending on package download speed
- Re-running the analysis after setup: roughly under one minute on the validated machine

## Repository structure

- `data/data/`: committed raw and logged World Bank tables
- `data/processed/`: modeling-ready dataset used by the analysis scripts
- `data/visuals/`: committed figures already produced for the project
- `src/`: analysis scripts and small reproducibility helpers
- `output/tables/`: generated result tables from the reproducible run

## Reproducibility notes

This repository intentionally keeps the existing analysis scripts intact and wraps them with small reproducibility helpers instead of rewriting the research code. The most important paper-vs-repo caveats, including the current estimation sample, are documented in `REPLICATION_NOTES.md`.

## Visual outputs

The visual outputs are generated by running:

python scripts/create_visuals.py

The figures are saved in:

output/figures/

Main figures:

- gdp_trends_by_country.png: shows log GDP trends for the six CEE countries.
- female_employment_trends_by_country.png: shows female employment trends over time.
- female_employment_vs_gdp.png: shows the relationship between female employment and GDP.
- correlation_matrix.png: shows correlations between the main model variables.

These figures support the interpretation of the data before discussing the SUR regression results.


