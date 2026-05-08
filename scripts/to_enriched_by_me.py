"""Extract incomplete enriched rows for manual completion."""

from __future__ import annotations

from netflix_utils import PROCESSED_DIR, load_latest_enriched_file, timestamp

OPTIONAL_METADATA_COLUMNS = ["catalog_title", "director", "country", "listed_in", "duration", "rating", "release_year"]


def main() -> None:
    df = load_latest_enriched_file()
    missing_optional_cols = [col for col in OPTIONAL_METADATA_COLUMNS if col not in df.columns]
    if missing_optional_cols:
        raise KeyError(f"Missing expected metadata columns: {missing_optional_cols}")

    incomplete = df[
        df[OPTIONAL_METADATA_COLUMNS].isna().all(axis=1)
        & df["corrected_type"].isin(["TV Show", "Movie"])
        & ~df["is_technical_asset_title"].fillna(False)
    ].copy()

    print(f"Nombre de lignes incomplètes détectées : {len(incomplete)}")
    if not incomplete.empty:
        print(incomplete[["Title", "Matched_Title", "corrected_type"]].head(10))

    output_file = PROCESSED_DIR / f"incomplete_titles_custom_{timestamp()}.csv"
    incomplete.to_csv(output_file, index=False)
    print(f"✅ Incomplete rows saved: {output_file}")


if __name__ == "__main__":
    main()
