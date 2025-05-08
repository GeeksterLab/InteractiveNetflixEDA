# scripts/classifier_history.py

import os
import glob
import re
from datetime import datetime
import pandas as pd

def select_enriched_file():
    """Sélectionne le fichier enriched_netflix_history dont la date est la plus proche d'aujourd'hui."""
    directory = "data/processed/"
    files = glob.glob(os.path.join(directory, "enriched_netflix_history_*.csv"))
    pattern = r"enriched_netflix_history_(\d{8}_\d{6})\.csv"
    file_dates = []
    for f in files:
        basename = os.path.basename(f)
        match = re.search(pattern, basename)
        if match:
            date_str = match.group(1)
            file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            file_dates.append((f, file_date))
    if not file_dates:
        raise FileNotFoundError("Aucun fichier enriched_netflix_history trouvé dans le dossier.")
    now = datetime.now()
    closest_file, closest_date = min(file_dates, key=lambda x: abs(now - x[1]))
    print(f"Chargement du fichier : {closest_file} (date extraite : {closest_date})")
    return closest_file

def main():
    # Charger le fichier enrichi dynamique
    enriched_file = select_enriched_file()
    df = pd.read_csv(enriched_file)

    # # S'assurer que la colonne "Date Watched" est au format datetime
    # df["Date Watched"] = pd.to_datetime(df["Date Watched"], format="%d/%m/%Y", errors="coerce")

    # Supprimer le format pour qu'il détecte automatiquement la date
    df["Date Watched"] = pd.to_datetime(df["Date Watched"], errors="coerce")

    # Supprimer les lignes sans date
    df = df[df["Date Watched"].notna()]

    # Forcer les dates entre 2015 et 2025
    min_date = pd.to_datetime("2015-01-01")
    max_date = pd.to_datetime("2025-12-31")
    df.loc[df["Date Watched"] < min_date, "Date Watched"] = min_date
    df.loc[df["Date Watched"] > max_date, "Date Watched"] = max_date

    # Grouper par "Title" et agréger les informations
    result = df.groupby("Title").agg(
        corrected_type=("corrected_type", "first"),
        duration=("duration", "first"),
        watched_min=("Date Watched", "min"),
        watched_max=("Date Watched", "max"),
        nombre_de_fois=("Title", "size")
    ).reset_index()

    # Trier par nombre_de_fois décroissant
    result = result.sort_values(by="nombre_de_fois", ascending=False)

    # Afficher un aperçu
    print(result.head(50))
    print(f"\nNombre total de titres agrégés : {len(result)}")

    # Générer un timestamp pour des noms de fichiers uniques
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Sauvegarder dans un CSV
    output_file = f"data/processed/titres_repetes_{timestamp}.csv"
    result.to_csv(output_file, index=False)
    print(f"\nFichier {output_file} enregistré avec succès.")

if __name__ == "__main__":
    main()
