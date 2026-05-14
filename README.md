# Evaluation of the Impact of Women's Employment on GDP in CEE Countries

## Authors

- Dawid Grzesiak 473172
- Kostiantyn Okhrimenko 473494
- Zarina Khalilova 476692
- Nyasha Nyarirangwe 474895

## What this repository reproduces

This repository reproduces the Python implementation of the Seemingly Unrelated Regression (SUR) analysis used for the project based on `Women's unemployment.pdf` by Asli Okay Toprak (2025). The study examines Hungary, Czechia, Poland, Romania, Bulgaria, and Greece over the 1992-2022 period, using GDP as the dependent variable and female employment, urban population, trade, and final consumption expenditure as explanatory variables.

The current presentation-day run reproduces the modeling stage from the committed processed dataset in `data/processed/panel_data.csv`. A separate notebook-based workflow for collecting raw World Bank data is also included in the repository.
It also regenerates a small set of script-based figures from that same committed processed dataset. The raw World Bank API collection step remains separate from the presentation-day run.

## Paper and replication scope

- Target paper: `Women's unemployment.pdf`
- Econometric approach: SUR with country-specific equations
- Main modeling entrypoint: `src/run_analysis.py`
- Figure-generation script: `scripts/create_visuals.py`
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
.\.venv\Scripts\python scripts\create_visuals.py
```

This sequence will:

1. Clone the repository into a fresh folder
2. Create an isolated Python environment with `virtualenv`
3. Install the pinned Python dependencies
4. Sync the committed logged dataset into the modeling input path
5. Run the diagnostics, SUR model, paper comparison, and robustness scripts
6. Generate the reproducible visual outputs in `output/figures/`

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

The scripted run also generates PNG figures in `output/figures/`:

- `gdp_trends_by_country.png`
- `female_employment_trends_by_country.png`
- `female_employment_vs_gdp.png`
- `correlation_matrix.png`

The repository also includes older committed notebook-based figures in `data/visuals/` as a legacy reference set.

## Expected runtime

- First run with environment setup: usually a few minutes, depending on package download speed
- Re-running the analysis after setup: roughly under one minute on the validated machine

## Repository structure

- `data/data/`: committed raw and logged World Bank tables
- `data/processed/`: modeling-ready dataset used by the analysis scripts
- `data/visuals/`: older committed notebook-based figures already produced for the project
- `scripts/`: helper scripts for validation and reproducible figure generation
- `src/`: analysis scripts and small reproducibility helpers
- `output/figures/`: reproducible figures generated from `scripts/create_visuals.py`
- `output/tables/`: generated result tables from the reproducible run

## Reproducibility notes

This repository intentionally keeps the existing analysis scripts intact and wraps them with small reproducibility helpers instead of rewriting the research code. The most important paper-vs-repo caveats, including the current estimation sample, are documented in `REPLICATION_NOTES.md`.

## Visual outputs

The presentation-day workflow regenerates four script-based figures in `output/figures/` from the committed processed dataset:

- `gdp_trends_by_country.png`: shows log GDP trends for the six countries
- `female_employment_trends_by_country.png`: shows female employment trends over time
- `female_employment_vs_gdp.png`: shows the relationship between female employment and GDP
- `correlation_matrix.png`: shows correlations between the main model variables

These figures support the interpretation of the data before discussing the SUR regression results.
The older notebook-based figures in `data/visuals/` remain in the repository as a legacy reference set, but `output/figures/` is now the canonical scripted figure output path.


