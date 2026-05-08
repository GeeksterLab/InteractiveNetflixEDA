"""Generate global Netflix viewing analysis charts."""

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


def prepare_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")
    return df.dropna(subset=["Date Watched"])


def plot_monthly_views(df: pd.DataFrame) -> None:
    monthly = df.resample("ME", on="Date Watched").size()
    plt.figure(figsize=(12, 6))
    monthly.plot(kind="bar")
    title = "Monthly Netflix Viewing Frequency"
    plt.title(title)
    plt.xlabel("Month")
    plt.ylabel("Number of Views")
    plt.xticks(range(0, len(monthly), 3), monthly.index.strftime("%Y-%m")[::3], rotation=45)
    plt.tight_layout()
    save_visualization(title)


def plot_movie_duration(df: pd.DataFrame) -> None:
    movies = df[df["corrected_type"] == "Movie"].copy()
    movies["duration_minutes"] = pd.to_numeric(
        movies["duration"].astype(str).str.replace(" min", "", regex=False), errors="coerce"
    )
    movies = movies.dropna(subset=["duration_minutes"])
    if movies.empty:
        print("⚠️ No valid movie duration data found.")
        return

    plt.figure(figsize=(10, 5))
    sns.histplot(movies["duration_minutes"], bins=20, kde=True)
    title = "Distribution of Movie Durations Watched"
    plt.xlabel("Duration (minutes)")
    plt.ylabel("Count")
    save_visualization(title)


def plot_weekly_habits(df: pd.DataFrame) -> None:
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    counts = df["Date Watched"].dt.day_name().value_counts().reindex(order, fill_value=0)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=counts.index, y=counts.values)
    title = "Netflix Watching Frequency by Day of Week"
    plt.xlabel("Day of Week")
    plt.ylabel("Number of Views")
    save_visualization(title)


def plot_yearly_trends(df: pd.DataFrame) -> None:
    counts = df["Date Watched"].dt.year.value_counts().sort_index()
    plt.figure(figsize=(8, 5))
    counts.plot(kind="line", marker="o")
    title = "Netflix Viewing Trends by Year"
    plt.xlabel("Year")
    plt.ylabel("Number of Views")
    plt.tight_layout()
    save_visualization(title)


def plot_release_vs_watch(df: pd.DataFrame) -> None:
    plot_df = df.copy()
    plot_df["release_year"] = pd.to_numeric(plot_df["release_year"], errors="coerce")
    plot_df["Year Watched"] = plot_df["Date Watched"].dt.year
    plot_df = plot_df.dropna(subset=["release_year", "Year Watched"])
    if plot_df.empty:
        print("⚠️ No valid release/watch year data found.")
        return

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=plot_df, x="release_year", y="Year Watched")
    title = "Relation between Content Release Year and Watching Year"
    plt.xlabel("Content Release Year")
    plt.ylabel("Year Watched")
    save_visualization(title)


PLOT_FUNCS = [
    plot_monthly_views,
    plot_movie_duration,
    plot_weekly_habits,
    plot_yearly_trends,
    plot_release_vs_watch,
]


def main() -> None:
    df = prepare_dates(load_latest_enriched_file())
    for plot_func in PLOT_FUNCS:
        plot_func(df)


if __name__ == "__main__":
    main()
