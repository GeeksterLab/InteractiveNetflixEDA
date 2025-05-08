# tests/unit/test_visualize_analyse_data.py

import pandas as pd
import runpy
import scripts.visualize_analyse_data as vad  # importe le module réel

def test_viz_data(tmp_path, monkeypatch):
    # 1) Prépare un faux CSV dans data/processed
    proc = tmp_path / "data" / "processed"
    proc.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({
        "Date Watched": ["2025-01-01 00:00:00"],
        "corrected_type": ["Movie"],
        "duration": ["100 min"],
        "release_year": [2020]
    })
    (proc / "enriched_netflix_history_20250101_000000.csv") \
        .write_text(df.to_csv(index=False))

    # 2) On travaille depuis tmp_path
    monkeypatch.chdir(tmp_path)

    # 3) On redirige save_path vers tmp_path/viz
    target = tmp_path / "viz"
    target.mkdir()
    monkeypatch.setattr(vad, "save_path", str(target))

    # 4) On exécute le module en tant que script
    runpy.run_module("scripts.visualize_analyse_data", run_name="__main__")

    # 5) Assert : au moins un .png créé
    files = list(target.glob("*.png"))
    assert files, f"Aucun .png généré dans {target}"
