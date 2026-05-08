"""Generate top-title Netflix charts."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from netflix_utils import VISUALIZATION_DIR, load_latest_enriched_file, safe_filename

sns.set_theme(style="darkgrid")


def save_visualization(title: str) -> None:
    VISUALIZATION_DIR.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(title)
    plt.savefig(VISUALIZATION_DIR / filename, bbox_inches="tight")
    plt.close()
    print(f"✅ Chart saved: {filename}")


def plot_top_counts(counts: pd.Series, title: str, xlabel: str) -> None:
    if counts.empty:
        print(f"⚠️ No data for: {title}")
        return
    plt.figure(figsize=(12, 6))
    counts.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Number of Views")
    plt.xticks(rotation=90)
    plt.tight_layout()
    save_visualization(title)


def main() -> None:
    df = load_latest_enriched_file().copy()
    df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")
    df = df.dropna(subset=["Date Watched"])

    title_column = "catalog_title" if "catalog_title" in df.columns else "Title"
    df["analysis_title"] = df[title_column].fillna(df["Title"]).fillna(df["Title"])

    movies = df[df["corrected_type"] == "Movie"]
    series = df[df["corrected_type"] == "TV Show"]

    plot_top_counts(series["analysis_title"].value_counts().head(20), "Top 20 Most Watched TV Shows", "TV Show Title")
    plot_top_counts(movies["analysis_title"].value_counts().head(20), "Top 20 Most Watched Movies", "Movie Title")

    df["Year Watched"] = df["Date Watched"].dt.year
    for year in sorted(df["Year Watched"].dropna().astype(int).unique()):
        yearly = df[df["Year Watched"] == year]
        plot_top_counts(
            yearly["analysis_title"].value_counts().head(10),
            f"Top 10 Most Watched Titles in {year}",
            "Title",
        )

    df["Month Watched"] = df["Date Watched"].dt.to_period("M")
    for month in sorted(df["Month Watched"].dropna().unique()):
        monthly = df[df["Month Watched"] == month]
        plot_top_counts(
            monthly["analysis_title"].value_counts().head(10),
            f"Top 10 Most Watched Titles in {month}",
            "Title",
        )


if __name__ == "__main__":
    main()
