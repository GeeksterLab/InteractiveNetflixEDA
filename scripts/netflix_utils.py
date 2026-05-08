"""Shared helpers for the Netflix EDA pipeline.

This module keeps title cleaning, path handling and file discovery in one place.
Yes, because copy-pasting the same glob/re/Path logic in eight scripts is how bugs breed.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

try:
    from rapidfuzz import fuzz, process
except ImportError:  # The rest of the pipeline can still run with exact matching only.
    fuzz = None
    process = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
VISUALIZATION_DIR = PROJECT_ROOT / "visualization"
REPORTS_DIR = PROJECT_ROOT / "reports"
CSS_PATH = PROJECT_ROOT / "assets" / "css" / "style.css"

ENRICHED_PATTERN = re.compile(r"enriched_netflix_history_(\d{8}_\d{6})\.csv$")

CATALOG_FILES = [
    RAW_DIR / "netflix_titles.csv",
    RAW_DIR / "netflix_movies_to_2025.csv",
    RAW_DIR / "netflix_tv_shows_to_2025.csv",
    RAW_DIR / "my_netflix_titles.csv",
]

REQUIRED_HISTORY_COLUMNS = ["Title", "Start Time"]
CATALOG_COLUMNS = ["title", "director", "country", "listed_in", "duration", "rating", "release_year"]

TECHNICAL_ASSET_PATTERN = re.compile(
    r"\b(?:hook|primary|secondary|16x9|9x16|1x1|clip|villain|hero|trailer|teaser|preview|"
    r"promo|recap|dub|sub|branded|clean|textless|vertical|horizontal)\b",
    flags=re.IGNORECASE,
)

SERIES_PATTERN = re.compile(
    r"\b(?:saison|season|partie|episode|épisode|ep\.?|mini-série|mini-serie|mini-épisode|pilot)\b",
    flags=re.IGNORECASE,
)

QUOTE_PATTERN = re.compile(r"[\"“”‘’]")
SPACES_PATTERN = re.compile(r"\s+")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_project_dirs() -> None:
    for directory in [RAW_DIR, PROCESSED_DIR, VISUALIZATION_DIR, REPORTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def clean_title(value: object) -> str:
    """Light cleaning that preserves the human-readable title."""
    if value is None:
        return ""

    if isinstance(value, float) and pd.isna(value):
        return ""

    title = str(value).strip()
    title = QUOTE_PATTERN.sub("", title)
    title = title.replace("Partie", "Saison").replace("partie", "saison")
    title = title.replace("\u00A0", " ")
    return SPACES_PATTERN.sub(" ", title).strip()

def is_technical_asset_title(title: str) -> bool:
    """
    Détecte les titres techniques Netflix qui ne sont pas de vrais contenus vus :
    hooks, clips, trailers, teasers, assets 16x9, backfill, etc.
    """
    if not isinstance(title, str):
        return False

    text = title.lower().strip()

    technical_patterns = [
        r"_hook",
        r"hook_",
        r"hook primary",
        r"hook_primary",
        r"primary_16x9",
        r"16x9",
        r"backfill",
        r"\bclip\b",
        r"_clip",
        r"clip_",
        r"\bteaser\b",
        r"bande-annonce",
        r"\btrailer\b",
        r"\bpromo\b",
        r"pvs clip",
        r"baseline clip",
        r"maincharacter",
        r"var\d+-clip",
    ]

    return any(re.search(pattern, text) for pattern in technical_patterns)

# def strip_episode_details(title: str) -> str:
#     """Return the catalog-level title from a Netflix viewing-history title."""
#     title = clean_title(title)

#     # Some exported rows may look like "date,title" after bad preprocessing.
#     if "," in title and re.match(r"^\d{4}-\d{2}-\d{2}", title):
#         title = title.split(",", 1)[1].strip()

#     title = re.sub(r"\(.*?\)", "", title).strip()
#     title = re.sub(r"\s*:\s*\d{4}\s*$", "", title).strip()
#     title = re.sub(r"\s*-\s*Saison\s*\d+\s*$", "", title, flags=re.IGNORECASE).strip()

#     # Netflix series rows are often "Show: Season 1: Episode title".
#     # For catalog matching, the show name is before the first colon.
#     parts = [p.strip() for p in title.split(":") if p.strip()]

#     # 🔥 garder la partie la plus "propre"
#     for part in parts:
#         if not re.search(r"(hook|clip|trailer|teaser|promo|16x9|backfill)", part, re.IGNORECASE):
#             return part

#     # fallback
#     return parts[0] if parts else title

def strip_episode_details(title: str) -> str:
    title = clean_title(title)

    if "," in title and re.match(r"^\d{4}-\d{2}-\d{2}", title):
        title = title.split(",", 1)[1].strip()

    title = re.sub(r"\(.*?\)", "", title).strip()
    title = re.sub(r"\s*:\s*\d{4}\s*$", "", title).strip()

    parts = [part.strip() for part in title.split(":") if part.strip()]

    bad_part_pattern = re.compile(
        r"^(saison|season)\s*\d+|"
        r"^(episode|épisode)\s*\d+|"
        r"^bande-annonce|"
        r"hook|clip|trailer|teaser|promo|16x9|backfill|cannotlocalize|noglobalvideo",
        flags=re.IGNORECASE,
    )

    for part in parts:
        if not bad_part_pattern.search(part):
            return re.sub(
                r"\s*[-:]?\s*(saison|season)\s*\d+\s*$",
                "",
                part,
                flags=re.IGNORECASE,
            ).strip()

    fallback = re.sub(
        r"\s*[-:]?\s*(saison|season)\s*\d+\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    return fallback

def normalize_title_key(value: object) -> str:
    """Create a stable matching key. This is stricter than fuzzy matching."""
    title = clean_title(value).lower()
    title = re.sub(r"&", " and ", title)
    title = re.sub(r"[^a-z0-9À-ÿ]+", " ", title)
    title = SPACES_PATTERN.sub(" ", title).strip()
    return title


# def is_probably_technical_asset_title(title: object) -> bool:
#     """Detect rows like hook_primary_16x9 / CLIP_VILLAIN that are not real catalog titles."""
#     cleaned = clean_title(title)
#     if not cleaned:
#         return False

#     snake = cleaned.replace("_", " ").replace("-", " ")
#     tokens = [token for token in re.split(r"\W+", snake.lower()) if token]
#     if not tokens:
#         return False

#     technical_hits = sum(bool(TECHNICAL_ASSET_PATTERN.search(token)) for token in tokens)
#     return technical_hits >= max(1, len(tokens) // 2)


# def infer_content_type(history_title: object, catalog_type: object = None) -> str:
#     if isinstance(catalog_type, str) and catalog_type.strip():
#         return catalog_type.strip()
#     title = clean_title(history_title)
#     return "TV Show" if SERIES_PATTERN.search(title) else "Movie"

def is_probably_technical_asset_title(title: object) -> bool:
    cleaned = clean_title(title)
    if not cleaned:
        return False

    text = cleaned.lower()

    # 🔥 Détection directe (plus brute, plus efficace)
    if re.search(
        r"(?i)(_hook|hook_|clip|teaser|trailer|promo|preview|16x9|9x16|1x1|backfill|villain|hero|cannotlocalize|noglobalvideo|no-global-video)",
        text,
    ):
        return True

    # 🔥 fallback intelligent (ton ancienne logique)
    tokens = re.split(r"\W+", text)
    tokens = [t for t in tokens if t]

    if not tokens:
        return False

    technical_hits = sum(bool(TECHNICAL_ASSET_PATTERN.search(t)) for t in tokens)

    return technical_hits >= max(1, len(tokens) // 2)

def select_latest_enriched_file(processed_dir: Path = PROCESSED_DIR) -> Path:
    candidates: list[tuple[Path, datetime]] = []
    for file_path in processed_dir.glob("enriched_netflix_history_*.csv"):
        match = ENRICHED_PATTERN.search(file_path.name)
        if match:
            file_date = datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
            candidates.append((file_path, file_date))

    if not candidates:
        raise FileNotFoundError(f"No enriched Netflix history file found in {processed_dir}")

    return max(candidates, key=lambda item: item[1])[0]


def load_latest_enriched_file() -> pd.DataFrame:
    file_path = select_latest_enriched_file()
    print(f"📄 Loading enriched file: {file_path}")
    return pd.read_csv(file_path)


def safe_filename(title: str, suffix: str = ".png") -> str:
    cleaned = normalize_title_key(title).replace(" ", "_")
    return f"{cleaned}{suffix}"


def validate_columns(df: pd.DataFrame, required_columns: Iterable[str], dataset_name: str) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise KeyError(f"{dataset_name} is missing required columns: {missing}")


def fuzzy_match_key(query_key: str, choices: list[str], threshold: int = 92) -> tuple[str | None, int | None]:
    """Return a fuzzy fallback match only when the score is high enough."""
    if not query_key or not choices or process is None or fuzz is None:
        return None, None

    match = process.extractOne(query_key, choices, scorer=fuzz.token_set_ratio)
    if not match:
        return None, None

    matched_key, score, _ = match
    if score >= threshold:
        return matched_key, int(score)
    return None, int(score)

def infer_content_type(history_title: object, catalog_type: object = None) -> str:
    if isinstance(catalog_type, str) and catalog_type.strip():
        return catalog_type.strip()

    title = clean_title(history_title)

    if re.search(
        r"(saison|season|episode|épisode|partie|mini-série|mini-serie|pilot)",
        title,
        re.IGNORECASE,
    ):
        return "TV Show"

    return "Movie"
