import pandas as pd
import runpy
from datetime import datetime

def test_to_enriched(tmp_path, monkeypatch, capsys):
    proc = tmp_path/"data"/"processed"; proc.mkdir(parents=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    f = proc/f"enriched_netflix_history_{now}.csv"
    pd.DataFrame({
      "Title":["A"],"Matched_Title":["A"],"corrected_type":["Movie"],
      "director":["D"],"country":["C"],"listed_in":["L"],"duration":[10],
      "rating":["R"],"release_year":[2025],"Date Watched":["2025-01-01"]
    }).to_csv(f,index=False)
    monkeypatch.chdir(tmp_path)
    runpy.run_module("to_enriched_by_me", run_name="__main__")
    out = capsys.readouterr().out
    assert "incomplètes détectées : 0" in out
