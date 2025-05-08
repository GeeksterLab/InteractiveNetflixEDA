import os
import pytest
import pandas as pd
from datetime import datetime, timedelta

from scripts import classifier_history

def test_select_enriched_file_no_files(tmp_path, monkeypatch):
    d = tmp_path / "data" / "processed"
    d.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        classifier_history.select_enriched_file()

def test_select_enriched_file_closest(tmp_path, monkeypatch, capsys):
    d = tmp_path / "data" / "processed"
    d.mkdir(parents=True)
    now = datetime.now()
    f1 = d / f"enriched_netflix_history_{(now - timedelta(days=1)).strftime('%Y%m%d_%H%M%S')}.csv"
    f2 = d / f"enriched_netflix_history_{(now - timedelta(days=2)).strftime('%Y%m%d_%H%M%S')}.csv"
    f1.write_text("") ; f2.write_text("")
    monkeypatch.chdir(tmp_path)

    res = classifier_history.select_enriched_file()
    assert os.path.abspath(res) == os.path.abspath(str(f1))
    out = capsys.readouterr().out
    assert "Chargement du fichier" in out

def test_main_writes_report(tmp_path, monkeypatch):
    d = tmp_path / "data" / "processed"
    d.mkdir(parents=True)
    df = pd.DataFrame({
        "Title": ["X","X","Y"],
        "corrected_type": ["Movie","Movie","TV Show"],
        "duration": [5,5,10],
        "Date Watched": [
            pd.Timestamp("2025-01-01"),
            pd.Timestamp("2025-01-02"),
            pd.Timestamp("2025-01-03")
        ]
    })
    enriched = d / "enriched_netflix_history_20250101_000000.csv"
    df.to_csv(enriched, index=False)
    monkeypatch.chdir(tmp_path)

    class FixedDT(datetime):
        @classmethod
        def now(cls):
            return datetime(2025,1,1,12,0,0)
    monkeypatch.setattr(classifier_history, "datetime", FixedDT)

    classifier_history.main()

    outputs = list(d.glob("titres_repetes_20250101_120000.csv"))
    assert len(outputs) == 1
    out_df = pd.read_csv(outputs[0])
    assert set(out_df["Title"]) == {"X","Y"}
