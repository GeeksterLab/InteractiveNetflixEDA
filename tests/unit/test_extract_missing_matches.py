import pandas as pd
import runpy
import pytest
from datetime import datetime

def test_extract_missing(tmp_path, monkeypatch, capsys):
    # Create the necessary directory structure
    data_dir = tmp_path / "data"
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame({
        "Matched_Title": [None, "A", None],
        "Date Watched": ["2025-01-01","2025-01-02","2025-01-03"],
        "Title": ["X","Y","Z"]
    })
    fake = processed_dir / "enriched_netflix_history_20250101_000000.csv"
    df.to_csv(fake, index=False)
    monkeypatch.chdir(tmp_path)

    # stub pandas.read_csv
    monkeypatch.setattr("pandas.read_csv", lambda f: df)
    class FD(datetime):
        @classmethod
        def now(cls): return datetime(2025,1,1)
    monkeypatch.setattr("scripts.extract_missing_matches.datetime", FD)

    runpy.run_module("scripts.extract_missing_matches", run_name="__main__")
    out = capsys.readouterr().out
    assert "⚠️ 2 titres n'ont pas été appariés" in out
    
    # Check that output files exist in the correct location
    missing_files = list(processed_dir.glob("missing_matches*.csv"))
    assert len(missing_files) == 1
    
    # Check file contents
    output_df = pd.read_csv(missing_files[0])
    assert len(output_df) == 2
    assert "X" in output_df["Title"].values and "Z" in output_df["Title"].values
    assert "Y" not in output_df["Title"].values
