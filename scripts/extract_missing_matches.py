"""Extract unmatched titles from the latest enriched Netflix history file."""

from __future__ import annotations

from netflix_utils import PROCESSED_DIR, load_latest_enriched_file, timestamp


def main() -> None:
    df = load_latest_enriched_file()
    missing = df[df["catalog_title"].isna() & ~df["is_technical_asset_title"].fillna(False)].copy()

    output_file = PROCESSED_DIR / f"missing_matched_titles_{timestamp()}.csv"
    missing.to_csv(output_file, index=False)

    print(f"⚠️ {len(missing)} non-technical titles are still unmatched.")
    if not missing.empty:
        print(missing[["Date Watched", "Title", "match_method", "match_score"]].head(10))
    print(f"✅ Debug file saved: {output_file}")


if __name__ == "__main__":
    main()
