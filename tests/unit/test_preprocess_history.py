import pandas as pd
import csv
import pytest
from scripts.preprocess_history import preprocess_csv

def test_preprocess_csv(tmp_path, capsys):
    input = tmp_path / "in.csv"
    df = pd.DataFrame({
        "Title": ['"Quote"', 'Partie 1', 'Normal']
    })
    df.to_csv(input, index=False, quoting=csv.QUOTE_ALL)
    output = tmp_path / "out.csv"

    preprocess_csv(str(input), str(output))
    out_df = pd.read_csv(output)
    assert out_df.loc[0, "Title"] == "Quote"
    assert out_df.loc[1, "Title"] == "Saison 1"
    captured = capsys.readouterr().out
    assert "Les guillemets ont été supprimés" in captured
