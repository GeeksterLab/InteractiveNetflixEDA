import pandas as pd
import runpy

from scripts import visualize_analyse_top_data

def test_viz_top(tmp_path, monkeypatch):
    proc = tmp_path/"data"/"processed"; proc.mkdir(parents=True)
    df = pd.DataFrame({
      "Date Watched": pd.to_datetime(["2025-01-01"]),
      "Title":["A","A","B"]
    })
    (proc/"enriched_netflix_history_20250101_000000.csv").write_text(df.to_csv(index=False))
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(visualize_analyse_top_data, "save_path", str(tmp_path/"viz"))
    (tmp_path/"viz").mkdir()
    runpy.run_module("visualize_analyse_top_data", run_name="__main__")
    assert list((tmp_path/"viz").glob("*.png"))
