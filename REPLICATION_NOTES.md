# Replication Notes

## Purpose

This file documents the current reproducible state of the repository without changing the underlying analysis logic. It is meant to clarify what the repository currently reproduces, what it does not yet automate, and where the results differ from the reference paper.

## Study being replicated

The target paper is `Women's unemployment.pdf` by Asli Okay Toprak (2025). The paper estimates a SUR model for:

- Hungary
- Czechia
- Poland
- Romania
- Bulgaria
- Greece

using annual World Bank data for 1992-2022.

The model relates:

- dependent variable: `lgdp`
- explanatory variables: `lerf`, `lup`, `ltrd`, `lfce`

## Current runnable workflow in this repository

The repository currently supports two related but separate workflows:

1. Optional raw-data collection and transformation in `data/collection_preprocessing.ipynb`
2. Scripted modeling in `src/run_analysis.py`

The notebook writes the logged dataset to `data/data/wdi_wide_logged.csv`. The modeling scripts read `data/processed/panel_data.csv`. To make that handoff explicit, this repository now includes `src/sync_processed_data.py`.

## Why the current SUR sample differs from the paper's headline period

The paper describes the study period as 1992-2022. However, the current Python implementation balances the SUR sample to the years available across all six countries after complete-case filtering.

In practice, the current scripts use a common sample beginning in 1995 because Poland starts later after missing values are dropped. This is implemented in `src/sur_model.py` and `src/robustness_checks.py` through the balanced-sample logic.

## Why some significance results differ from the paper

When this repository was re-run in a clean Python environment on May 14, 2026, the female-employment coefficients were:

- Hungary: significant positive
- Czechia: significant positive
- Poland: not significant
- Romania: significant negative
- Bulgaria: significant positive
- Greece: significant negative

This differs from the paper's summary, where Romania and Greece are reported as statistically insignificant for female employment.

Possible reasons include:

- the balanced 1995-2022 estimation sample rather than a nominal 1992-2022 window
- implementation differences between the paper's original workflow and the current Python workflow
- robust covariance settings in the current `linearmodels` SUR implementation
- preprocessing choices embedded in the committed dataset

This repository does not claim that the timespan difference is the only reason for the discrepancy. It is simply one plausible contributor that should be kept in mind when interpreting the replication results.

## Data source note

The paper describes the female variable as the World Bank employment-to-population ratio for women aged 15+ using modeled ILO estimates. The current repository documentation has been aligned to that variable description.

## What was intentionally not changed

To respect the original project work, the following were intentionally left conceptually unchanged:

- the existing analysis scripts in `src/`
- the current variable transformations
- the SUR model structure
- the committed datasets and figures already present in the repository

The changes in this reproducibility pass focus on documentation, environment pinning, explicit workflow handoffs, presentation helpers, and generated output tracking.
