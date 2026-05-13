from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data" / "data" / "wdi_wide_logged.csv"
TARGET_PATH = ROOT / "data" / "processed" / "panel_data.csv"

REQUIRED_COLUMNS = [
    "country_code",
    "country",
    "year",
    "lgdp",
    "lerf",
    "lup",
    "ltrd",
    "lfce",
]


def validate_columns(df):
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in source dataset: {missing}")


def main():
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {SOURCE_PATH}. "
            "Run the collection notebook first or restore the committed data files."
        )

    df = pd.read_csv(SOURCE_PATH)
    validate_columns(df)

    if TARGET_PATH.exists():
        current = pd.read_csv(TARGET_PATH)
        validate_columns(current)

        if df.equals(current):
            print(f"Processed dataset already synchronized: {TARGET_PATH}")
            return

    TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(TARGET_PATH, index=False)

    print(f"Synchronized processed dataset to: {TARGET_PATH}")


if __name__ == "__main__":
    main()
