"""Clean and merge Netflix viewing history with Netflix catalog metadata.

Main output:
- data/processed/enriched_netflix_history_<timestamp>.csv

Debug outputs:
- debug_unmatched_titles_<timestamp>.csv
- debug_technical_asset_titles_<timestamp>.csv
"""

from __future__ import annotations

import csv
import pandas as pd

from netflix_utils import (
    CATALOG_COLUMNS,
    CATALOG_FILES,
    PROCESSED_DIR,
    RAW_DIR,
    clean_title,
    ensure_project_dirs,
    fuzzy_match_key,
    infer_content_type,
    is_probably_technical_asset_title,
    normalize_title_key,
    strip_episode_details,
    timestamp,
    validate_columns,
)


def load_netflix_catalog() -> pd.DataFrame:
    frames = []
    for path in CATALOG_FILES:
        if path.exists():
            print(f"📚 Catalog found: {path}")
            frames.append(pd.read_csv(path))

    if not frames:
        raise FileNotFoundError("No Netflix catalog file found in data/raw.")

    catalog = pd.concat(frames, ignore_index=True)
    validate_columns(catalog, ["title"], "Netflix catalog")

    for column in CATALOG_COLUMNS:
        if column not in catalog.columns:
            catalog[column] = pd.NA

    catalog["catalog_title"] = catalog["title"].apply(clean_title)
    catalog["catalog_key"] = catalog["catalog_title"].apply(normalize_title_key)
    catalog = catalog.drop_duplicates(subset=["catalog_key"], keep="first")
    return catalog


def prepare_history(path=RAW_DIR / "ViewingActivity.csv") -> pd.DataFrame:
    history = pd.read_csv(path)
    validate_columns(history, ["Title", "Start Time"], "ViewingActivity")

    history["Title"] = history["Title"].apply(clean_title)
    history = history.dropna(subset=["Title", "Start Time"]).copy()
    history["Matched_Title"] = history["Title"].apply(strip_episode_details)
    history["history_key"] = history["Matched_Title"].apply(normalize_title_key)
    history = history[history["Matched_Title"].str.len() > 3]
    history["is_technical_asset_title"] = history["Title"].apply(
        is_probably_technical_asset_title
    )

    return history


def apply_fuzzy_fallback(merged: pd.DataFrame, catalog: pd.DataFrame) -> pd.DataFrame:
    unresolved_mask = merged["catalog_title"].isna() & ~merged["is_technical_asset_title"]
    if not unresolved_mask.any():
        merged["match_score"] = merged.get("match_score", pd.NA)
        return merged

    catalog_by_key = catalog.set_index("catalog_key")
    catalog_keys = catalog_by_key.index.dropna().tolist()

    fuzzy_keys = []
    fuzzy_scores = []
    for query_key in merged.loc[unresolved_mask, "history_key"]:
        matched_key, score = fuzzy_match_key(query_key, catalog_keys)
        fuzzy_keys.append(matched_key)
        fuzzy_scores.append(score)

    merged.loc[unresolved_mask, "fuzzy_catalog_key"] = fuzzy_keys
    merged.loc[unresolved_mask, "match_score"] = fuzzy_scores

    fuzzy_mask = merged["fuzzy_catalog_key"].notna()
    if not fuzzy_mask.any():
        return merged

    columns_to_fill = ["catalog_title", "type", "director", "country", "listed_in", "duration", "rating", "release_year"]
    for row_index, fuzzy_key in merged.loc[fuzzy_mask, "fuzzy_catalog_key"].items():
        catalog_row = catalog_by_key.loc[fuzzy_key]
        for column in columns_to_fill:
            if column in merged.columns and column in catalog_row.index and pd.isna(merged.at[row_index, column]):
                merged.at[row_index, column] = catalog_row[column]
        merged.at[row_index, "match_method"] = "fuzzy"

    return merged


def build_enriched_history() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ensure_project_dirs()
    history = prepare_history()
    catalog = load_netflix_catalog()

    technical_history = history[history["is_technical_asset_title"]].copy()
    history = history[~history["is_technical_asset_title"]].copy()

    merged = history.merge(
        catalog,
        left_on="history_key",
        right_on="catalog_key",
        how="left",
        suffixes=("_history", "_catalog"),
    )
    merged["match_method"] = merged["catalog_title"].notna().map({True: "exact", False: "unmatched"})
    merged["match_score"] = pd.NA
    # merged = apply_fuzzy_fallback(merged, catalog)

    merged["corrected_type"] = merged.apply(
        lambda row: infer_content_type(row["Title"], row.get("type")), axis=1
    )

    enriched_columns = [
        "Start Time",
        "Title",
        "Matched_Title",
        "catalog_title",
        "corrected_type",
        "director",
        "country",
        "listed_in",
        "duration",
        "rating",
        "release_year",
        "match_method",
        "match_score",
        "is_technical_asset_title",
    ]
    enriched = merged[enriched_columns].copy()
    enriched = enriched.rename(
        columns={
            "Start Time": "Date Watched",
            "Title": "raw_title",
            "Matched_Title": "Title",
        }
    )

    required_cols = ["Title", "Date Watched", "corrected_type"]
    enriched = enriched.dropna(subset=required_cols)

    unmatched = enriched[
        (enriched["catalog_title"].isna()) &
        (~enriched["Title"].str.contains(
            r"(?i)(hook|clip|trailer|teaser|promo|16x9|backfill)",
            na=False
        ))
    ].copy()
    technical_assets = technical_history.copy()

    return enriched, unmatched, technical_assets


def main() -> None:
    print("🔄 Building enriched Netflix history...")
    enriched, unmatched, technical_assets = build_enriched_history()
    run_id = timestamp()

    enriched_path = PROCESSED_DIR / f"enriched_netflix_history_{run_id}.csv"
    enriched.to_csv(enriched_path, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"✅ Enriched history saved: {enriched_path}")

    if not unmatched.empty:
        unmatched_path = PROCESSED_DIR / f"debug_unmatched_titles_{run_id}.csv"
        unmatched.to_csv(unmatched_path, index=False)
        print(f"⚠️ Unmatched titles saved: {unmatched_path} ({len(unmatched)} rows)")

    if not technical_assets.empty:
        assets_path = PROCESSED_DIR / f"debug_technical_asset_titles_{run_id}.csv"
        technical_assets.to_csv(assets_path, index=False)
        print(f"🧩 Technical asset titles saved: {assets_path} ({len(technical_assets)} rows)")


if __name__ == "__main__":
    main()
