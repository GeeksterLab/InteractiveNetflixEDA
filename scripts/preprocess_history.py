"""Preprocess Netflix ViewingActivity.csv.

Output: data/raw/ViewingActivity_clean.csv
"""

from __future__ import annotations

import csv

import pandas as pd

from netflix_utils import RAW_DIR, clean_title, ensure_project_dirs, validate_columns


def preprocess_csv(input_file=RAW_DIR / "ViewingActivity.csv", output_file=RAW_DIR / "ViewingActivity_clean.csv") -> pd.DataFrame:
    ensure_project_dirs()
    df = pd.read_csv(input_file, encoding="utf-8")
    validate_columns(df, ["Title"], "ViewingActivity")

    df["Title"] = df["Title"].apply(clean_title)
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"✅ Clean history saved to: {output_file}")
    return df


if __name__ == "__main__":
    preprocess_csv()
