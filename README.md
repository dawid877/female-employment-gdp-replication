# Evaluation of the Impact of Women's Employment on GDP in CEE Countries: A Replication of Toprak (2025)

## Group Members

- Name 1 - Architect
- Name 2 - Wrangler
- Name 3 - Analyst
- Name 4 - Lead Author

## Research Question

To what extent did female employment rates affect GDP in Hungary, Czechia, Poland, Romania, Bulgaria, and Greece between 1992 and 2022?

## Project Overview

This repository supports a reproducible replication project on the relationship between women's employment and macroeconomic performance in Central and Eastern Europe. The project focuses on reproducing the empirical strategy described in `Women's unemployment.pdf` and adapting it to a transparent Python-based workflow suitable for collaborative research.

## Data Sources

The analysis will rely on World Bank Open Data indicators:

- GDP (constant 2015 US$): [NY.GDP.MKTP.KD](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD)
- Female Employment Ratio: [SL.TLF.CACT.FE.ZS](https://data.worldbank.org/indicator/SL.TLF.CACT.FE.ZS)
- Urban Population: [SP.URB.TOTL.IN.ZS](https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS)
- Trade (% of GDP): [NE.TRD.GNFS.ZS](https://data.worldbank.org/indicator/NE.TRD.GNFS.ZS)
- Final Consumption Expenditure: [NE.CON.TOTL.KD](https://data.worldbank.org/indicator/NE.CON.TOTL.KD)

## Planned Approach

We will replicate the Seemingly Unrelated Regression (SUR) framework described in `Women's unemployment.pdf` to estimate how female employment relates to GDP across the selected countries. The workflow will apply natural log transformations to the main variables, including `lgdp`, `lerf`, and related controls, to align the specification with the original econometric design and to address correlation across country-level error terms.

## Motivation

The project is motivated by two goals. First, it tests the "feminization U" theory in a regional CEE context by examining whether increases in women's employment are associated with economic growth. Second, it demonstrates how regional econometric modeling can be organized in a clean, reproducible research environment that supports collaboration, inspection, and re-execution.

## Repository Structure

- `data/` stores raw data inputs and data-fetching scripts.
- `src/` stores Python scripts for cleaning, transformation, and econometric analysis.
- `output/` stores rendered figures, tables, and reports.

## Reproducibility Conventions

All project code should use relative paths built with `pathlib` and should avoid absolute local file paths to keep the workflow portable across machines and collaborators.
