"""Aggregate enriched Netflix history by title."""

from __future__ import annotations

import pandas as pd

from netflix_utils import PROCESSED_DIR, load_latest_enriched_file, timestamp


def classify_repeated_titles(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")
    df = df[df["Date Watched"].notna()]

    result = (
        df.groupby("Title", dropna=False)
        .agg(
            display_title=("Title", "first"),
            catalog_title=("catalog_title", "first"),
            corrected_type=("corrected_type", "first"),
            duration=("duration", "first"),
            watched_min=("Date Watched", "min"),
            watched_max=("Date Watched", "max"),
            nombre_de_fois=("Title", "size"),
        )
        .reset_index()
        .sort_values(by="nombre_de_fois", ascending=False)
    )
    return result


def main() -> None:
    df = load_latest_enriched_file()
    result = classify_repeated_titles(df)
    print(result.head(50))
    print(f"\nNombre total de titres agrégés : {len(result)}")

    output_file = PROCESSED_DIR / f"titres_repetes_{timestamp()}.csv"
    result.to_csv(output_file, index=False)
    print(f"✅ Repeated-title summary saved: {output_file}")


if __name__ == "__main__":
    main()
