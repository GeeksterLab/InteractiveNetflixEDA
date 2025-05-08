import os
import pandas as pd
import pytest
from scripts.clean_merge_data import (
    load_netflix_data,
    clean_title,
    simplify_title,
    extract_matched_title,
    match_titles,
    categorize_title,
    extract_season,
)

def make_csv(tmp_path, name, df):
    path = tmp_path / name
    df.to_csv(path, index=False)
    return path

def test_load_netflix_data_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.clean_merge_data.file_paths", [str(tmp_path/"nofile.csv")])
    with pytest.raises(FileNotFoundError):
        load_netflix_data()

def test_load_netflix_data_success(tmp_path, monkeypatch):
    df1 = pd.DataFrame({"foo":[1]})
    df2 = pd.DataFrame({"foo":[2]})
    p1 = make_csv(tmp_path, "a.csv", df1)
    p2 = make_csv(tmp_path, "b.csv", df2)
    monkeypatch.setattr("scripts.clean_merge_data.file_paths", [str(p1), str(p2)])
    monkeypatch.setattr("os.path.exists", lambda x: True)
    df = load_netflix_data()
    pd.testing.assert_frame_equal(df.reset_index(drop=True),
                                  pd.concat([df1, df2], ignore_index=True))

def test_clean_and_simplify_match_extract_and_categorize_and_season():
    title = '“My Show: Partie 2” (Episode)'
    cleaned = clean_title(title)
    assert '“' not in cleaned and 'Partie' not in cleaned and 'Saison 2' in cleaned

    simplified = simplify_title("Fear Street - Saison 1 : 1994")
    assert simplified == "Fear Street"

    matched = extract_matched_title("2025-03-30 14:48:01,Some Title: Extra")
    assert matched == "Some Title"

    netflix = ["some title","other"]
    assert match_titles("Some Title", netflix) == "some title"
    assert match_titles("", netflix) is None

    assert categorize_title("Show Saison 1", {}) == "TV Show"
    assert categorize_title("MovieTitle", {}) == "Movie"

    assert extract_season("Series Saison 3: Ep") == 3
    assert extract_season("NoSeasonHere") is None
